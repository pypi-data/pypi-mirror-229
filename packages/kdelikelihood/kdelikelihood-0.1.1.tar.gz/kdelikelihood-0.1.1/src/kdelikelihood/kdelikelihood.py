"""
Created on 01.03.2021

@author: fischsam
"""
import os
import threading
from warnings import warn

from scipy import stats
from scipy.integrate import odeint
from scipy.interpolate import interp1d

import matplotlib.pyplot as plt
import numpy as np

from objectproxypool import ProxyPool, SharedArrayWrapper, unpack
from objectproxypool.pool import get_chunksize_per_worker

CPU_COUNT = os.cpu_count()
odeLock = threading.Lock()

from ._kde_tools import ElementaryLikelihoodComputer


def get_bandwidth_by_silverman(data, nanVal=np.nan, dataGroups=1, sampleSize=None):
    """
    Returns kernel density bandwidths based on a Rule of thumb
    by Silverman, B.W.: Density estimation for statistics and data analysis (Eq. 3.28)
    for Gaussialn kernels.

    Parameters
    ----------
    data : float[][]
        Array of multivariate observations
    nanVal : float
        Value for non-existent / not applicable observations
    dataGroups : int
        Number of independent groups that the data will be split into
    sampleSize : float
        Size of the sample for which the bandwidth is sought. If `None`,
        the size of the provided data is used.

    """
    if np.isnan(nanVal):
        data = np.ma.array(data, mask=np.isnan(data))
    elif nanVal:
        data = np.ma.array(data)
        data[data == nanVal] = np.ma.masked

    if sampleSize is None:
        sampleSize = data.shape[0]

    return np.maximum(
        1.06
        * np.asarray(np.std(data, axis=0))
        * (sampleSize / dataGroups) ** (-1 / (4 + data.shape[1])),
        1e-7,
    )


class NoBiasCorrectionFunction:
    """
    Dummy function not correcting any bias.

    Can be used instead of `BiasCorrectionFunction` if nothing
    should be done.
    """

    def __call__(self, x, sampleSize=None):
        return x


class BiasCorrectionFunction:
    """
    Function correcting the bias introduced in the
    kernel density estimate by taking the logarithm.

    The idea is to use a first order approimation for the bias
    and variance. The resulting correction term is derived
    by solving an ODE.
    """

    def __init__(
        self,
        integralsOfSquaredKernels,
        sampleSize=None,
        step=0.001,
        x0=(0, 1),
        minArg=-20,
        steadyStateTolerance=1e-14,
    ):
        """
        Initializer

        Parameters
        ----------
        integralsOfSquaredKernels : float[]
            Array containing the squared integral of the
            kernels used in each dimension. Note that
            the kernel depends on the bandwidth here!
        sampleSize : int
            Size of the sample used to estimate the likelihood.
            This can also be provided later when calling the function.
        step : float
            step size for the solution of the ODE
        x0 : (float, float)
            Initial condition of the ODE. (x(0), x'(0)) This can be changed to
            minimize the mean squared error. The default value is typically good.
            Note that the function becomes discontinueous unless x0[0] = 0 and
            undifferentiable unless x0[1] = 1.
        minArg : float
            Guess for the minimal argument with which this function will be called.
            The guess will be adjusted if necessary.
        steadyStateTolerance : float
            For small arguments, the ODE, which approaches a steady state as x->-inf,
            may not need to be solved. Instead the value of the steady state
            could be used.
        """
        self._prefactor = 2 / np.asarray(integralsOfSquaredKernels).prod()
        self.step = step
        self.x0 = x0
        self.minArg = minArg
        self.sampleSize = sampleSize
        self._hasReachedSteadyState = False
        self.steadyStateTolerance = steadyStateTolerance
        if sampleSize:
            self.update_ode()

    def set_sample_size(self, sampleSize):
        if self.sampleSize == sampleSize:
            return
        self.sampleSize = sampleSize
        self.update_ode()

    def update_ode(self):
        factor = self._prefactor * self.sampleSize

        self.odeFun = lambda xx, tt: (xx[1], (tt - xx[0]) * factor * np.exp(tt) + xx[1])
        self.odeGrad = lambda _, tt: ((0, 1), (-factor * np.exp(tt), 1))
        self.update_solution()

    def update_solution(self):
        t = np.arange(0, self.minArg - self.step / 2, -self.step)

        with odeLock:
            solution = odeint(self.odeFun, self.x0, t, Dfun=self.odeGrad)

        self.solution = interp1d(t[::-1], solution[::-1, 0])
        self._hasReachedSteadyState = np.allclose(
            self.odeFun(solution[-1], self.minArg), 0, atol=self.steadyStateTolerance
        )

    def __call__(self, x, sampleSize=None):
        if sampleSize:
            self.set_sample_size(sampleSize)

        minX = np.min(x)
        for _ in range(20):
            if minX > self.minArg or self._hasReachedSteadyState:
                break
            self.minArg *= 2
            self.update_solution()
        else:
            warn(
                "BiasCorrectionFunction is called for a small argument "
                "but the steady state has not been reached within the given "
                "time. The returned values may be wrong."
            )

        # Since we know that the ODE has an asymptote as x->-infinity,
        # we can approximate small values.
        if minX < self.minArg:
            x = np.maximum(x, self.minArg)

        if np.max(x) > 0:
            if np.isscalar(x):
                return np.log(x)
            result = np.empty_like(x)
            result[x >= 0] = x[x >= 0]
            result[x < 0] = self.solution(x[x < 0])
            return result

        return self.solution(x)


class LikelihoodComputer:
    def __init__(
        self,
        observations,
        weights,
        bandwidths,
        domains=0,
        consideredColumns=None,
        atol=1e-5,
        guaranteedLookupDistance=None,
        transformData=True,
        correctBias=True,
    ):
        if hasattr(domains, "__iter__"):
            domains = np.asarray(domains, dtype=np.int32, order="C")
        elif domains:
            domains = np.full(observations.shape[1], domains, dtype=np.int32, order="C")

        bandwidths = np.asarray(bandwidths)
        if np.isscalar(bandwidths):
            bandwidths = np.full_like(domains, bandwidths, dtype=float)

        if guaranteedLookupDistance is None:
            guaranteedLookupDistance = -np.log(atol)

        self.__guaranteedLookupDistance = guaranteedLookupDistance
        self.__inverseBandwidths = inverseBandwidths = 1 / bandwidths
        self.__transformData = transformData

        if transformData:
            observations = observations * inverseBandwidths

        if consideredColumns is None:
            consideredColumns = np.arange(len(bandwidths))
        elif not len(consideredColumns):
            raise ValueError("consideredColumns must contain at least one value.")

        # sort observations array for potentially improved performance
        order = np.lexsort(observations.T[consideredColumns[::-1]])
        observations = observations[order]
        weights = np.asarray(weights)[order]

        considered = np.zeros_like(observations, dtype=bool)
        considered[:, consideredColumns] = True
        considered &= np.isfinite(observations)

        consideredColumnKeys = list(
            (np.nonzero(row)[0], (considered == row).all(1))
            for row in np.unique(considered, axis=0)
        )

        if not consideredColumnKeys[0][0].size:
            raise ValueError("No data row is allowed to contain NaNs only.")

        kernelWidth = 120
        normalizations = np.zeros_like(bandwidths, dtype=float)
        integralsOfSquaredKernels = np.zeros_like(bandwidths, dtype=float)
        continuous = domains < 2
        kernelVars = bandwidths * bandwidths
        normalizations[continuous] = np.sqrt(2 * np.pi * kernelVars[continuous])
        integralsOfSquaredKernels[continuous] = 1 / (np.sqrt(np.pi) * 2 * bandwidths[continuous])
        normalizations[~continuous] = (
            np.exp(-np.arange(kernelWidth) ** 2 / (2 * kernelVars[~continuous][:, None]))
        ).sum(1) * 2 - 1
        integralsOfSquaredKernels[~continuous] = (
            np.exp(-np.arange(kernelWidth) ** 2 / (kernelVars[~continuous][:, None]))
        ).sum(1) * 2 - 1
        logNormalizations = np.log(normalizations)

        self.__elementaryLikelihoodComputers = {
            tuple(columns): ElementaryLikelihoodComputer(
                observations[rows],
                weights[rows],
                columns,
                domains,
                inverseBandwidths,
                logNormalizations[columns].sum(),
                guaranteedLookupDistance * len(columns) / len(consideredColumns),
                (
                    BiasCorrectionFunction(integralsOfSquaredKernels[columns])
                    if correctBias
                    else NoBiasCorrectionFunction()
                ),
            )
            for columns, rows in consideredColumnKeys
        }

    def compute_log_likelihood(self, sample):
        if self.__transformData:
            sample = sample * self.__inverseBandwidths

        return sum(
            elem.compute_log_likelihood(sample)
            for elem in self.__elementaryLikelihoodComputers.values()
        )


class MultipleDatasetLikelihoodComputer:
    def __init__(
        self,
        observations,
        weights,
        bandwidths,
        modes=0,
        consideredColumns=None,
        atols=1e-3,
        guaranteedLookupDistances=None,
        transformData=True,
        correctBias=True,
    ):
        if consideredColumns is None:
            consideredColumns = [None] * len(observations)
        self.consideredColumns = consideredColumns

        if np.isscalar(bandwidths):
            bandwidths = [bandwidths] * len(observations)
        self.bandwidths = bandwidths

        if np.isscalar(modes):
            modes = [modes] * len(observations)
        self.modes = modes

        if np.isscalar(atols):
            atols = [atols] * len(consideredColumns)
        self.atols = atols

        if np.isscalar(guaranteedLookupDistances) or guaranteedLookupDistances is None:
            guaranteedLookupDistances = [guaranteedLookupDistances] * len(consideredColumns)
        self.guaranteedLookupDistances = guaranteedLookupDistances

        self.likelihoodComputers = [
            LikelihoodComputer(
                obs, we, bw, m, consCol, atol, guaranteedLookupDistance, transformData, correctBias
            )
            for obs, we, bw, m, consCol, atol, guaranteedLookupDistance in zip(
                observations,
                weights,
                bandwidths,
                modes,
                consideredColumns,
                atols,
                guaranteedLookupDistances,
            )
        ]

    def compute_log_likelihood(self, sample):
        return sum(comp.compute_log_likelihood(sample) for comp in self.likelihoodComputers)


class RemoteMultipleDatasetLikelihoodComputer(MultipleDatasetLikelihoodComputer):
    def __init__(self, jobCounter=None):
        pass

    def init(self, args, kwargs={}):
        super().__init__(*args, **kwargs)
        return threading.get_native_id()

    def compute_log_likelihood(self, sample):
        return super().compute_log_likelihood(unpack(sample))


class ParallelLikelihoodComputer:
    """
    An object allowing to compute the KDE likelihood in parallel

    The object holds a set of field data and allows to estimimate
    their likelihood based on a set of model-generated data
    """

    def __init__(
        self,
        observations,
        bandwidths,
        domains=0,
        dataGroups=1,
        correctBias=True,
        atols=1e-3,
        guaranteedLookupDistances=None,
        numWorkers=None,
        separateProcesses=False,
    ):
        """
        Initializer

        Parameters
        ----------
        observations : float[][]
            Array containing the field data for which the likelihood
            should be computed. Each column represents a different data
            feature; each row represents a different observation
        bandwidths : float[]
            Array containing the bandwidth of the kernel density estimation
            for each data feature. The bandwidth should correspond to the
            scale of the data. Larger bandwidths reduce the stochasticity of
            the likelihood estimates; smaller bandwidths reduce the bias of the
            estimates.
        domains : int[]
            Array specifying the domains of the data features. A value of 0
            corresponds to unconstrained real numbers; a value of 1 to
            non-negative real numbers; a value of 2 to natural numbers.
        dataGroups : int
            Specifys into how many independent feature subsets the data set may
            be split. A value of 1 means that all features depend on one another;
            a value as high as the number of features indicates that all
            features are independent. Smaller values lead to correct likelihood
            estimates in the limit of infinite generated data; larger values
            lead to more robust an less bias estimates of the composite likelihood.
        correctBias : bool
            Whether to apply bias correction.
        atols : float[]
            Approximate tolerance (order of magnitude) for the computational error
            in the estimate. Smaller values result in higher accuracy; larger values
            in faster computation time. Can be specified for each data feature
            individually.
        numWorkers : int
            Number of separate threads or processes used. Default is the number of
            available CPUs.
        separateProcesses : weather to use seperate processes (multiprocessing) or
            separate threads (multithreading). The former is often better on systems
            with many (>10) CPUs and if large data sets are considered. The latter
            can be much faster otherwise due to reduced overhead.
        """
        if numWorkers is None:
            numWorkers = os.cpu_count()

        observations = np.asarray(observations)

        if dataGroups > observations.shape[1]:
            raise ValueError("We cannot consider more data groups than data features.")

        self.separateProcesses = separateProcesses

        observationCount, dataDim = observations.shape
        dataSectionLength = int(np.ceil(dataDim / dataGroups))
        dtype = observations.dtype
        if np.issubdtype(dtype, np.integer):
            dtype = np.double

        if np.isscalar(bandwidths):
            bandwidths = np.full(dataDim, bandwidths)
        else:
            bandwidths = np.asarray(bandwidths)

        observations = observations / bandwidths.astype(dtype)

        if np.isscalar(domains):
            domains = np.full(dataDim, domains)
        else:
            domains = np.asarray(domains)

        if np.isscalar(atols):
            atols = [atols] * dataGroups

        if np.isscalar(guaranteedLookupDistances) or guaranteedLookupDistances is None:
            guaranteedLookupDistances = [guaranteedLookupDistances] * dataGroups

        observationListRaw = []

        def argGenerator():
            # prepare data
            nonlocal observationListRaw
            observationListRaw = []
            colListRaw = []
            validObservationsList = []
            countsListRaw = []
            notExistentValue = np.nanmin(observations) - 1
            assert np.isfinite(notExistentValue)
            for i in range(dataGroups):
                # the considered columns
                col = np.arange(i * dataSectionLength, min((i + 1) * dataSectionLength, dataDim))

                # the considered data
                observations_ = observations[:, col].copy()

                # replace nans with some other value
                observations_[np.isnan(observations_)] = notExistentValue

                # remove duplicates (note: data get sorted!)
                _, uniqueIndices, counts = np.unique(
                    observations_, axis=0, return_index=True, return_counts=True
                )

                # shuffle for equal load on the processors
                randomOrder = np.arange(counts.size)
                np.random.shuffle(randomOrder)
                uniqueIndices = uniqueIndices[randomOrder]
                counts = counts[randomOrder]

                # store prepared data
                colListRaw.append(col)
                observationListRaw.append(observations[uniqueIndices].copy())
                validObservationsList.append(~np.isnan(observations[:, col][uniqueIndices]))
                countsListRaw.append(counts)

            # determine workload
            jobNumber = sum(validObservations.sum() for validObservations in validObservationsList)
            taskLengths = get_chunksize_per_worker(jobNumber, numWorkers)
            plannedCumTask = np.cumsum(taskLengths)

            dataIndex = 0  # the current position in the data set
            taskIndex = 0  # the number of already returned elements (tasks)
            scheduledTasks = 0  # the number of already processed rows
            addOne = True
            isNewTask = True

            # TODO: there may be a bug that sometimes causes an empty data set to be included.
            # this happens randomly based on sorting order (at least it looks like it).
            # Restarting helps in this case. A thorough fix is still required, though.

            for (
                col,
                observations_,
                validObservations,
                counts,
                atol,
                guaranteedLookupDistance,
            ) in zip(
                colListRaw,
                observationListRaw,
                validObservationsList,
                countsListRaw,
                atols,
                guaranteedLookupDistances,
            ):
                # process all rows for the current columns
                while dataIndex < observations_.shape[0]:
                    # if we have a fresh task, reset all the information
                    if isNewTask:
                        newlyScheduledTasks = 0
                        wantedTaskLength = taskLengths[taskIndex]
                        taskLength = 0
                        obs = []
                        cts = []
                        atols_ = []
                        cols = []
                        guaranteedLookupDistances_ = []
                        isNewTask = False

                    # look how many data we have to process
                    oldDataIndex = dataIndex
                    taskLengthChart = validObservations[oldDataIndex:].sum(1).cumsum()
                    additionalRowNumber = (
                        np.searchsorted(taskLengthChart, wantedTaskLength - newlyScheduledTasks)
                        + addOne
                    )

                    # we return at least one job
                    additionalRowNumber = max(additionalRowNumber, 1)

                    dataIndex += additionalRowNumber

                    # if we had added one, how many items would we have processed?
                    if additionalRowNumber - addOne < taskLengthChart.size:
                        potentialTaskLength = (
                            taskLength + taskLengthChart[additionalRowNumber - addOne]
                        )
                    else:
                        potentialTaskLength = taskLength + taskLengthChart[-1]

                    obs.append(observations_[oldDataIndex:dataIndex])
                    cts.append(counts[oldDataIndex:dataIndex])
                    cols.append(col)
                    atols_.append(atol)
                    guaranteedLookupDistances_.append(guaranteedLookupDistance)

                    # check how long the job is alreday (processing nans does not count)
                    newTaskCount = np.isfinite(obs[-1][:, col]).sum()
                    scheduledTasks += newTaskCount
                    taskLength += newTaskCount
                    newlyScheduledTasks += newTaskCount

                    # if the job is long enough
                    if (
                        potentialTaskLength >= wantedTaskLength
                        or plannedCumTask[taskIndex] == scheduledTasks
                    ):
                        # if we are not ahead of the schedule, make the task at least as long as wanted
                        addOne = scheduledTasks <= plannedCumTask[taskIndex]

                        # yield result
                        dataSetNumber = len(obs)
                        yield obs, cts, [bandwidths] * dataSetNumber, [
                            domains
                        ] * dataSetNumber, cols, atols_, guaranteedLookupDistances_, False, correctBias

                        # start a new task
                        taskIndex += 1
                        isNewTask = True
                        if dataIndex == observations_.shape[0]:
                            dataIndex = 0
                            break
                    else:
                        dataIndex = 0
                        break

        self.bandwidths = bandwidths.astype(dtype)

        arguments = list(argGenerator())
        self.likelihoodComputers = ProxyPool(
            RemoteMultipleDatasetLikelihoodComputer,
            min(numWorkers, len(arguments)),
            separateProcesses=separateProcesses,
        )
        assert len(arguments) == self.likelihoodComputers.numWorkers
        threadIDs = self.likelihoodComputers.init(
            arguments, synchronize_workers=True, map_args=True
        )
        if not np.unique(threadIDs).size == len(threadIDs):
            raise AssertionError(
                "One of the workers did not get initialized "
                "properly. The results will be wrong. "
                "This may be because one of the threads "
                "got stuck. Just try it again. If this issue occurs "
                "repeatedly, file an issue on the project's bug tracker."
            )

    def compute_log_likelihood(self, sample):
        if self.separateProcesses:
            sample = SharedArrayWrapper(sample)
            sample.array /= self.bandwidths
            return np.sum(
                self.likelihoodComputers.compute_log_likelihood(
                    sample.remoteArray, synchronize_workers=True
                )
            )
        else:
            sample = sample / self.bandwidths
            return np.sum(
                self.likelihoodComputers.compute_log_likelihood(sample, synchronize_workers=True)
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.likelihoodComputers.close()
