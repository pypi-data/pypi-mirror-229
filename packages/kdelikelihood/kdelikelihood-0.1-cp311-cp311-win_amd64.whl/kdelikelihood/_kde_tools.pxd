'''
Created on 19.04.2021

@author: fischsam
'''
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
cimport numpy as np


cdef extern from "_kde_tools_internals.h":
    struct VectorHasher:
        pass

    ctypedef long index_t;
    ctypedef vector[index_t] key_t;
    ctypedef unordered_map[key_t, vector[index_t], VectorHasher] map_t;
    
    map_t *construct_grid_float "construct_grid<float>"(float **observations, int *consideredColumns, int *mode, int dim, long lenObservations, float guaranteedLookupDistance) nogil
    map_t *construct_grid_double "construct_grid<double>"(double **observations, int *consideredColumns, int *mode, int dim, long lenObservations, double guaranteedLookupDistance) nogil
    
    void compute_log_likelihood_float "compute_log_likelihood<float>"(map_t &hashMap, float **observations, float **sample, int *consideredColumns, int *mode, float *inverseBandwidth, float logNormalization, int dim, long lenObservations, long lenSample, float guaranteedLookupDistance, float *out) nogil
    void compute_log_likelihood_double "compute_log_likelihood<double>"(map_t &hashMap, double **observations, double **sample, int *consideredColumns, int *mode, double *inverseBandwidth, double logNormalization, int dim, long lenObservations, long lenSample, double guaranteedLookupDistance, double *out) nogil
    
#     void print_timing()

cdef class ElementaryLikelihoodComputer:
    
    cdef: 
        map_t *grid
        float **observationsFloatPointer
        double **observationsDoublePointer
        np.ndarray observations
        np.ndarray consideredColumns 
        np.ndarray domains
        np.ndarray inverseBandwidth
        np.ndarray weights
        double logNormalization
        double guaranteedLookupDistance
        object dtype
        object biasCorrectionFunction
        long columnNumber