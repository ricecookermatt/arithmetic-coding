#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 13:52:45 2025

@author: matthew
"""

import numpy as np


"""
Arithmetic coding steps:
    1.  Read data
    2.  Compute the probability mass function of the data symbols
    3.  Compute the cumulative distribution function using the pmf
    4.  Perform decimal encoding to find the lower and upper interval bounds by
    iterating through the data symbols.
    5.  Take the midpoint (average) of the lower and upper bounds and perform
    binary encoding (converting to fixed point)
"""
    
#1. Read data
#-----------------------------------------------------------------------------
text = "DACDDBCD"
print(text, '\n')


#2. Compute PMF
#-----------------------------------------------------------------------------
symbol_list = []
symbol_count = []
total_symbols = len(text) #To convert counts into probabilities at the end
sym_pmf = [] #Will be a list of tuples

#Iterate through each character in the data and update lists
for character in text:
    #print(character) #DEBUG
    
    #Check if the character already exists in our list
    if (character in symbol_list):
        #Get position of existing character
        symbol_pos = symbol_list.index(character)
        
        #Increment the occurance count by 1
        symbol_count[symbol_pos] += 1
    else:
        #Add the new character to the end of our list
        symbol_list.append(character)
        
        #Initialize its count by 1
        symbol_count.append(1)
        
#Convert counts into probabilities
num_unique_symbols = len(symbol_count)

for i in range(num_unique_symbols):
    #Convert to empirical distribution
    symbol_count[i] /= total_symbols
    
    #Create a list of tuples using symbols and their pmf
    sym_pmf.append( (symbol_list[i], symbol_count[i]) )
    
    
#Sort the list in increasing pmf. Secondary sort by ASCII value in a pmf tie
sym_pmf.sort()

#print(sym_pmf) #DEBUG


#3. Compute CDF
#-----------------------------------------------------------------------------
cumsum = 0.0
cdf = [] #List of tuples

for j in range(0, num_unique_symbols):
    cumsum += sym_pmf[j][1] #Cumulatively add the pmf of the current symbol
    cdf.append( (sym_pmf[j][0], cumsum) )
    
#print(cdf) #DEBUG


#4. Perform decimal encoding
#-----------------------------------------------------------------------------
cdf_l = 0.0
cdf_h = 0.0

encoding_lower = 0.0
encoding_upper = 1.0

#Iterate over the data again
for character in text:
    
    #Search through our list of tuples to find the symbol and its cdf
    for pos in range(num_unique_symbols):
        
        #Brute force check through our list 
        if cdf[pos][0] == character:
            #Find upper CDF bound
            cdf_h = cdf[pos][1]
            
            #Instead of finding cdf_l by looking at index i-1 and worrying
            #about the special case where i=0 and get out-of-bounds error
            #Just calculate cdf_l directly
            
            #Find lower CDF bound
            cdf_l = cdf_h - sym_pmf[pos][1]
            
    
    #Get occupied length
    delta = encoding_upper - encoding_lower
            
    #"Zoom-in" within the occupied length and create a new sub-section
    encoding_upper = encoding_lower + delta*cdf_h
    
    #Need to update encoding_lower after encoding_upper since
    #blocking assignment and encoding_upper relies on encoding_lower
    
    #"Zoom-in" within the occupied length and create a new sub-section
    encoding_lower = encoding_lower + delta*cdf_l
    
#5. Perform binary encoding
#-----------------------------------------------------------------------------
#Place encoded value in the middle of the occupied section so the codeword
#is in the middle of the symbol distribution
#This adds an extra fractional binary point due to the additional precision
decimal_encoding = (encoding_upper + encoding_lower) / 2

#Determine number of bits
