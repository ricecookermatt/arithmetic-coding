#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 15:14:13 2025

@author: matthew

This Python script empirically determines the maximum number of bits required
when performing arithmetic coding (decimal codeword to binary conversion).


To put into Jupyter Notebook:
Constraints:
    Number of total characters in the data is a power of 2
    Number of unique characters is no more than 4
    Each character is i.i.d.
    
Theorized bound:
    Assuming worst case the data only contains characters that occur once,
    the encoding will perform N times on the same delta (which is equal to 
    the p.m.f.).  
    
    Where N = data length, M = # unique chars
    In the scenario described above, N = M and delta (pmf) is equal to 1/M

    -log2[ (1/M)^N ]

    Sign negation is due to pmf being fractional
    Use log2 since converting to binary
    
    
    Since the data is encoded in the middle between the bounds, an extra bit
    is required
    
    Theorized worst case number of bits: 1 + -log2[ (1/M)^N ] 
    To make more intuitive with the addition of the extra bit:
        
    1 + log2[ (1/M)^(-N) ]
    
   
    It can also be expressed as 1 + (N/M)*log2[ N^M ] = 1 + log2(N^N)
    Comment: Do the alphabet size doesn't matter?
    Need to check my assumption on the formulas raising pmf
    
"""

import numpy as np
import matplotlib.pyplot as plt
from arithmetic_coding import arithmetic_encode


#Testing begins here
#-----------------------------------------------------------------------------
#Num of combinations (assuming order matters): M^N
#N = data length, M = number of symbols

data_length = 8

num_unique_symbols = 2
symbols = np.arange(num_unique_symbols)

ratio = data_length / num_unique_symbols

theoretical_bound = np.int64(1 + ratio*np.log2( data_length**(num_unique_symbols) ) )
print("Theoretical bound:", theoretical_bound, "bits")


#Maximum number of combinations
max_sims = num_unique_symbols**data_length
num_bits = np.zeros(max_sims, dtype='int64')

#Create generator object
rng = np.random.default_rng()


for i in range(max_sims):
    #Randomize data using discrete uniform distribution
    data = rng.integers(0, max(symbols), data_length, endpoint=True)
    
    bin_code = arithmetic_encode(data)
    
    #Need to add 1 since start at 0 and subtract by 2 since string prefix '0b'
    min_bits = 1 + bin_code.rfind('1') - 2
    num_bits[i] = min_bits
    

empirical_bound = max(num_bits)
print("Empirical bound:", empirical_bound, "bits")

#Minimum number of bits will be 1 for the case where data is all 0's or 1's
#Need to add +1 to end of np.arange() because: 
#1) up to but not including
#2) histogram requires an additional point since specifying intervals
#Using this to set histogram bin width to 1
#First bin will be [1, 2)
#Second bin will be [2, 3)
#Third bin will be [3, 4)
bin_edges = np.arange(1, 25 + 1 + 1)


x = np.histogram(num_bits, bins=bin_edges, density=True)
plt.figure(1)
plt.bar(bin_edges[:-1], x[0], edgecolor = 'k')

#Find expected number of bits via dot product
#@ operator is shorthand for np.matmul()
#For N = 8, M = 8, E[X] rounded up = 21
avg_b = x[0] @ x[1][:-1]
print("Expected number of bits:", avg_b, "bits")

plt.xlabel("Minimum number of bits")
plt.ylabel("Probability")

title = f"Empirical Results from {max_sims} Simulations"
plt.title(title)

plt.grid()
plt.minorticks_on()

plt.xlim([0, 25+1])
plt.ylim([0, 1])
