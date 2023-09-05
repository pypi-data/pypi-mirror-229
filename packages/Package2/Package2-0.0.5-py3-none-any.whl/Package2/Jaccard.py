# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:59:12 2023

@author: ANASUA
"""
import numpy as np
from scipy.sparse import csr_matrix

# Jaccard similarity
def similarity(mat):
    A = csr_matrix(mat)
    At = csr_matrix(mat.T)
    
    # Computing the numerator X.Xt
    intersection = np.dot(A, At)
    
    # Computing the denominator (X.1m,n + (X.1m,n)t - X.Xt)
    ones = np.ones(csr_matrix(mat).shape[::-1])
    B = A.dot(ones)
    union = B + B.T - intersection
    
    # Calculated Jaccard's Matrix
    jaccard = np.round((intersection / union), 3)
    return jaccard
# Jaccard distance
def distance(mat):
    jaccard_index=similarity(mat)
    jd = np.ones(jaccard_index.shape[::-1]) - jaccard_index
    return jd