import numpy as np
from matplotlib import pyplot as plt
from scipy import stats


def normal_smoothing(functionValues, step, kernelStd=1):
    """
    Applies smoothing with a normal kernel to given function
    values via a discrete convolution.

    The output corresponds to the same x-values as the input.

    Parameters
    ----------
    functionValues : float[]
        Array with y-values of a function to be smoothed
    step : float
        Difference between the x-values belonging to adjacent
        entries of `data`.
    kernelStd : float
        Standard deviation of the smoothing kernel

    """
    kernelWidth = kernelStd * 5
    if step == 1:
        kernel = stats.norm.pdf(np.arange(2 * kernelWidth + 1), kernelWidth, kernelStd)
        kernel /= kernel.sum()
        result = np.convolve(functionValues, kernel, domains="same")
        return result
    kernel = stats.norm.pdf(np.arange(-kernelWidth, kernelWidth + step / 2, step), 0, kernelStd)
    kernel /= kernel.sum()
    result = np.convolve(functionValues, kernel, mode="same")
    return result

    result[kernelWidth] += result[:kernelWidth].sum()

    return result[kernelWidth:]


def generate_sample(
    model, observableFun, sampleSize=1000, burnIn=0, dt=1, runFun=None, **observableFunArgs
):
    """
    Generates a sample from a model by recording
    an observable in regular time intervals.

    Note: The model is assumed to be ergodic and in a steady state.
    The sample elements are not fully independent in general.

    Parameters
    ----------
    model : pyformind.Model
        Model from which the sample shall be generated
    observableFun : callable
        Function that takes a model instance and returns
        the observables of interest. May return a 1D array
        (results are assumed to be one sample from a
        random vector) or a 2D array (results are assumed
        to be independent samples from a random vector of the
        size of the first row.
    sampleSize : int
        Denotes how often `fun` is to be applied to `model`.
        Note that the size of the sample will be larger, if
        `fun` returns multiple observations.
    burnIn : int
        Denotes how long the model is run before the sample
        is taken
    dt : float
        Time step between two sampling points
    runFun : callable
        Function that takes a model instance and a time
        and runs the model for that time. If not provided
        or `None`, then `model.run()` will be used.
    **observableFunArgs : keyword arguments
        Keyword arguments passed to `fun`

    """
    if runFun is None:
        runFun = lambda _model, _dt: _model.run(_dt)

    if burnIn:
        for _ in range(int(np.ceil(burnIn / dt))):
            runFun(model, dt)

    runFun(model, dt)
    firstSample = observableFun(model, **observableFunArgs)

    if np.isscalar(firstSample):
        chunkSize, dim = 1, 1
        dtype = type(firstSample)
    else:
        firstSample = np.asarray(firstSample)
        if firstSample.ndim == 1:
            chunkSize, dim = 1, firstSample.size
        else:
            chunkSize, dim = firstSample.shape
        dtype = firstSample.dtype

    sample = np.zeros((sampleSize * chunkSize, dim), dtype=dtype)
    sample[:chunkSize] = firstSample

    for i in range(1, sampleSize):
        runFun(model, dt)
        sample[i * chunkSize : (i + 1) * chunkSize] = observableFun(model, **observableFunArgs)
    return sample


def plot_smoothened(
    data,
    bandwidth=None,
    bins=None,
    reflect=True,
    axis=None,
    shift=0,
    onlyHistogram=False,
):
    """
    Plots a histogram and a smoothed curve for a given data set

    Parameters
    ----------
    data : float[]
        Array with the data
    bandwidth : float
        Standard deviatiation of the applied Gaussian kernel
    bins : float[]
        Edges of bins or number of bins used for the histogram
    reflect : bool
        If `True`, reflecting boundary conditions are assumed.
    axis : axis
        Matplotlib axis object used for plotting.
    shift : float
        Shifts the data before plotting
    onlyHistogram : bool
        If `True`, only the histogram (no smoothed curve) will be plotted.

    """
    integral = (bins is not None and type(bins) == np.ndarray and bins.dtype == int) or (
        bins is None and not (data % 1).any()
    )

    if reflect:
        if integral:
            addedData = np.concatenate((data, -data[data != 0]))
        else:
            addedData = np.concatenate((data, -data))
        addedData += shift
    else:
        addedData = data

    data += shift

    if integral:
        bins = np.arange(data.min() - 0.5, data.max() + 0.5)
    elif bins is None:
        bins = min(max(data.size // 50, 20), 500)

    if bandwidth is None:
        if integral:
            bandwidth = 1
        else:
            bandwidth = 0.01

    if axis is None:
        axis = plt.gca()

    values, bins = axis.hist(data, bins=bins, density=True, alpha=0.5)[:2]

    if not onlyHistogram:
        if not integral:
            bins = 1000

        y, smoothingBins = np.histogram(addedData[np.isfinite(addedData)], bins=bins, density=True)[
            :2
        ]

        if reflect and not integral:
            y *= 2

        color = axis.containers[-1].patches[0].get_facecolor()
        smoothened = normal_smoothing(y, smoothingBins[1] - smoothingBins[0], bandwidth)

        smoothingBins = smoothingBins + (smoothingBins[1] - smoothingBins[0]) / 2
        axis.plot(smoothingBins[:-1], smoothened[-y.size :], color=(*color[:-1], 1))

    if reflect:
        axis.set_xlim((shift, None))

    if not onlyHistogram:
        return smoothingBins[:-1], smoothened[-y.size :]
    else:
        return bins[:-1], values


def analyze_distribution(fun, args=[], kwargs={}, n=10, verbose=True):
    """Return mean, standard deviation, and span of repeated evaluations of a function

    Parameters
    ----------
    fun : callable
        funciton to analyze
    args : list, optional
        list of arguments, by default []
    kwargs : dict, optional
        dictionary of keyword arguments, by default {}
    n : int, optional
        number of function evaluations, by default 10
    verbose : int, optional
        if True, print the information; if >= 2, also print the
        result of each function evaluation. By default True

    Returns
    -------
    tuple[float, float, float]
        mean, standard deviation, and span of the function return values
    """
    results = []
    for _ in range(n):
        result = fun(*args, **kwargs)
        results.append(result)
        if verbose >= 2:
            print(result)

    mean = np.mean(results)
    std = np.std(results, ddof=1)
    span = np.max(results) - np.min(results)
    if verbose:
        print("Mean     = {:7.3f}".format(mean))
        print("Std. dev = {:7.3f}".format(std))
        print("Span     = {:7.3f}".format(span))

    return mean, std, span
