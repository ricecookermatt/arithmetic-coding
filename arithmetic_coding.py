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

"""

    
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
        
        
    #Sort the list in ascending order
    char_pmf.sort()
    
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