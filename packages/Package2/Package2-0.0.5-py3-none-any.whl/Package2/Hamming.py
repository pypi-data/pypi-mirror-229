# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:47:48 2023

@author: ANASUA
"""

def distance(string1,string2): ## input: string1 and string2 of same length
     
    if len(string1) != len(string2):
        raise ValueError("Input strings must have the same length")
        
    else:
        
        distance = 0  # Start with a distance of zero
    
        L = len(string1)  ## length of the strings
        for i in range(L): # Loop over the indices of the string
    
           if string1[i] != string2[i]:   ## if the two characters of same indices are not equal
                distance = distance + (2**(L-(i+1)))
    return distance ## Return the Hamming distance between string1 and string2, i.e. the 