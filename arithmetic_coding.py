#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 13:52:45 2025

@author: matthew

This Python script performs lossless data compression using arithmetic coding

Arithmetic coding steps on a fixed length of data:
    1.  Compute the probability mass function of the data symbols
    2.  Compute the cumulative distribution function using the pmf
    3.  Perform decimal encoding to find the lower and upper interval bounds by
    iterating through the data symbols.
    4.  Take the midpoint (average) of the lower and upper bounds and perform
    binary encoding (converting to fixed point)
    
    
TO-DO:
    --Utilize Python any() and count() function for calculating pmf
    --Look into using dictionaries instead of a list of tuples
    --Look into using Counter from collections
    --Clean up decimal encode/decode to not rely on pmf
    --Instead of iteratively checking a binary string for decode, use
    a dot product method

"""

from collections import Counter
from itertools import accumulate

#-----------------------------------------------------------------------------
# Encoding
#-----------------------------------------------------------------------------

text = 'ADBAACBA'

#1. Pythonic way to calculate empirical distributions (pmf and cdf)
def compute_distributions(data):
    histogram = Counter(data)
    
    total = histogram.total()
    #total = len(data)
    
    for key in histogram:
        histogram[key] /= total
    
    return histogram

hist = compute_distributions(text)
hist_keys = hist.keys()
hist_values = hist.values()

pmf = hist.most_common() #Give a sorted list based on the counts
pmf.sort(key=lambda pmf: (pmf[1], pmf[0]) ) #Sort by counts first then item





#1. Compute PMF
#-----------------------------------------------------------------------------
def compute_pmf(text):
    #Input: List of data or a string
    #Output: List of tuples which contain the symbols and their pmf
    
    char_list = []
    char_count = []
    
    #Iterate through each character in the text and update lists
    for character in text:
        
        #Check if the character already exists in our list
        if (character in char_list):
            #Get position of existing character
            list_pos = char_list.index(character)
            
            #Increment the occurance count by 1
            char_count[list_pos] += 1
        else:
            #Add the new character to the end of our list
            char_list.append(character)
            
            #Initialize its count by 1
            char_count.append(1)          


    #Convert counts into probabilities
    total_char = len(text) #To convert counts into probabilities
    char_pmf = []
    
    for i in range( len(char_list) ):
        #Convert to empirical distribution
        char_count[i] /= total_char
        
        #Create a list of tuples using symbols and their pmf
        char_pmf.append( (char_list[i], char_count[i]) )
        
        
    #Sort the list in ascending order based on pmf (second element)
    char_pmf.sort(key=lambda char_pmf: char_pmf[1])
    
    return char_pmf


#2. Compute CDF
#-----------------------------------------------------------------------------
def compute_cdf(char_pmf):
    #Input: List of tuples which contain the symbols and their pmf
    #Output: List of tuples which contain the symbols and their cdf
    
    cumsum = 0.0
    char_cdf = []
    
    for j in range( len(char_pmf) ):
        #Cumulative sum
        cumsum += char_pmf[j][1]
        
        #Create a list of tuples using symbols and their cdf
        char_cdf.append( (char_pmf[j][0], cumsum)  )
    
    return char_cdf


#3. Perform decimal encoding
#-----------------------------------------------------------------------------
def decimal_encode(text, char_pmf, char_cdf):
    #Input: List of data or a string, pmf list of tuples, cdf  list of tuples
    #Output: Decimal representation of arithmetic encoding

    cdf_l = 0.0
    cdf_h = 0.0
    
    encoding_lower = 0.0
    encoding_upper = 1.0
    
    #Iterate over the data again
    for character in text:
        
        #any('A' in sublist for sublist in cdf)
        
        #Search through our list of tuples to find the symbol and its cdf
        for pos in range( len(char_pmf) ):
            
            #Brute force check through our list 
            if char_cdf[pos][0] == character:
                #Find upper CDF bound
                cdf_h = char_cdf[pos][1]
                
                #Instead of finding cdf_l by looking at index i-1 and worrying
                #about the special case where i=0 and get out-of-bounds error
                #Just calculate cdf_l directly
                
                #Find lower CDF bound
                cdf_l = cdf_h - char_pmf[pos][1]
                
        
        #Get occupied length
        delta = encoding_upper - encoding_lower
                
        #"Zoom-in" within the occupied length and create a new sub-section
        encoding_upper = encoding_lower + delta*cdf_h
                
        #Need to update encoding_lower after encoding_upper since
        #blocking assignment and encoding_upper relies on encoding_lower
        
        #"Zoom-in" within the occupied length and create a new sub-section
        encoding_lower = encoding_lower + delta*cdf_l
    
    #Place encoded value in the middle of the occupied section so the codeword
    #is in the middle of the symbol distribution
    #This adds an extra fractional binary point due to the additional precision    
    decimal_encoding = (encoding_upper + encoding_lower) / 2
    
    return decimal_encoding

    
#4. Perform binary encoding
#-----------------------------------------------------------------------------
def binary_encode(decimal_code):
    #Input: Decimal coded input between 0 and 1
    #Output: Unsigned Fixed-point binary coded output (UQ0.25 format)
    
    '''
    #Based on theoretical and empirical calculations
    upper_bit_bound = 25
    
    
    cumsum = 0.0
    binary_encoding = ''
    
    #Perform successive approximation to converge to the binary representation
    for i in range(1, upper_bit_bound + 1):
        
        if (cumsum + 2**(-i) > decimal_code):
            #If went over, then do not contribute this fractional bit
            binary_encoding += '0'
        else:
            #If did not go over, then contribute this fractional bit
            cumsum += 2**(-i)
            binary_encoding += '1'
    '''
    
    #Give output in consitent number of bits by scaling by 2^25
    #Scale by 25 bits because that is the WC bound for N=8
    #For performing empirical testing, scale by a larger number to avoid
    #any possible loss of precision
    fxp_int = int( decimal_code * (2**25) )
    binary_encoding = bin(fxp_int)
        
    return binary_encoding

#Group helper functions
#-----------------------------------------------------------------------------
def arithmetic_encode(text):
    pmf = compute_pmf(text)
    cdf = compute_cdf(pmf)
    
    dec_code = decimal_encode(text, pmf, cdf)
    bin_code = binary_encode(dec_code)
    
    return bin_code

#-----------------------------------------------------------------------------
# Decoding
#-----------------------------------------------------------------------------

#1. Perform decimal decoding
#-----------------------------------------------------------------------------
def binary_decode(binary_code):
    #Input: Arithmetic coded 25-bit binary string with prefix '0b'
    #Output: Arithmetic code in decimal
    
    #Remove '0b' prefix
    binary_string = binary_code[2:]
    
    dec_val = 0.0
    
    #Convert from binary to decimal
    for string_pos in range(0, 25-1):
        
        if binary_string[string_pos] == '1':
            
            fract_pos = string_pos + 1
            dec_val += 2**(-fract_pos)
    
    return dec_val

#2. Perform arithmetic decoding
#-----------------------------------------------------------------------------
def decimal_decode(dec_val, pmf, cdf):
    #Input: Decimal coded input and its cdf and pmf
    #Output: Decoded text
    
    decoded_text = ''
    
    
    for data_pos in range(8):
        #Perform CDF check on dec_val
        for i in range( len(cdf) ):
            if (dec_val < cdf[i][1]):
                use_cdf_index = i
                
                #Update codeword
                dec_val = ( dec_val - (cdf[use_cdf_index][1] - pmf[use_cdf_index][1]) ) / pmf[use_cdf_index][1]
                decoded_text += cdf[use_cdf_index][0]
                
                #Finish for loop if we found our match early
                break
    
    return decoded_text

#Group helper functions
#-----------------------------------------------------------------------------
def arithmetic_decode(text, bin_code):
    pmf = compute_pmf(text)
    cdf = compute_cdf(pmf)
    
    dec_val = binary_decode(bin_code)
    data_recovered = decimal_decode(dec_val, pmf, cdf)
    
    return data_recovered


dat_a = '01010101'
dat_b = '10101010'

#If there is a tie, then CDF goes by order they appeared. Incorrect
code_a = arithmetic_encode(dat_a) #pmf = [('0', 0.5), ('1', 0.5)]
code_b = arithmetic_encode(dat_b) #pmf = [('1', 0.5), ('0', 0.5)]

x = arithmetic_decode(dat_a, code_a)
y = arithmetic_decode(dat_b, code_b)