import numpy as np
from numpy.lib.ufunclike import _deprecate_out_named_y
import scipy as stats
from scipy.signal import savgol_filter
import pandas as pd
from encoder import NumpyEncoder
from scipy.signal import argrelextrema
import os


class Tools():  
        
    #Read input file and convert it into useable data
    def processTXTContent(self, data, startIndex, xIndex, yIndex):
        arrayOfLines = data.splitlines()

        try:
            arrayOfLines = arrayOfLines[startIndex-1:]
        except:
            print("StartIndex out of bounds")
        splittedArrayOfLines = []
        for each in arrayOfLines:
            try:
                # tmp = list(map(float, each.split()))
                tmp = each.split()
                try:
                    x = float(tmp[xIndex-1])
                except:
                    print("Xindex out of bounds")
                try:
                    y = float(tmp[yIndex-1])
                except:
                    print("yIndex out of bounds")
                    
                t = [x,y]
                splittedArrayOfLines.append(t)

            except:
                print("Splitting did not really work")    

        x = [each[0] for each in splittedArrayOfLines]  
        y = [each[1] for each in splittedArrayOfLines]    

        return x,y

         
    # destructure chart.js data structure to a more accessible one    
    def unWrap(self, data):
        x = [each["x"] for each in data]  
        y = [each["y"] for each in data] 
        return x,y
    
    # convert back to chart.js accessible data
    def wrap(self, x, y):
        output = []
        
        for X,Y in zip(x,y):
            output.append({
                "x":X, "y":Y
            })

        return output
            
    # apply savgol filter to data, to minimize perturbations
    def cleanData(self, data, windowSize, degree):
        x,y = Tools.unWrap(self,data)

   
        newY = savgol_filter(y, windowSize, degree)
        result = Tools.wrap(self,x,newY)
        return result
    
    # calculate first degree polynomial
    def polynomialOne(coefficients, x):
        m = coefficients[0]
        b = coefficients[1]
        return m*x + b 

    # calculate fifth degree polynomial
    def polynomialFive(coefficients, x):
        m1 = coefficients[0]
        m2= coefficients[1]
        m3 = coefficients[2]
        m4 = coefficients[3]
        m5 = coefficients[4]
        b = coefficients[5]
        
        return (m1 * x**5)+(m2 * x**4)+(m3 * x**3)+(m4 * x**2)+(m5 * x) + b
    
    # Calibrate input data given calibration values
    def getCoefficients(self, regressionValues):
            
        pixels = []
        lambdas = []
        for id, values in regressionValues.items():               
            pixel = values[0]
            lam = values[1]

            pixels.append(pixel)
            lambdas.append(lam)            

        
        numberLambdas = len(lambdas)
        if numberLambdas == 2:
            fit = np.polyfit(pixels,lambdas,1)
        else:
            fit = np.polyfit(pixels,lambdas,5)
            
        return fit
    
    
    
    # apply calculated fit to the dataentries
    def applyCoefficients(self, x, coefficients):
        
        if len(coefficients) > 2: 
            newx = [Tools.polynomialFive(coefficients, i) for i in x]  
        else:
            newx = [Tools.polynomialOne(coefficients, i) for i in x]  
  
        
        return newx
    
    # pipe to the calculation of transmission and absorption
    def returnTransAndAbsorp(self, data, reference):
        dataX, dataY = Tools.unWrap(self, data)
        referenceX, referenceY = Tools.unWrap(self, reference)
        
        transmissionY = Tools.calculateTransmission(self, dataY, referenceY)
        absorptionY = Tools.calculateAbsorption(self, transmissionY)
    
        # transmission = Tools.wrap(self, dataX, transmissionY)
        # absorption = Tools.wrap(self, dataX, absorptionY)
        
        return dataX, transmissionY, absorptionY
    
    # calculate the transmission of a dataset given the reference measurement
    def calculateTransmission(self, data, reference):
        transmission = np.divide(data,reference)

        return transmission
        
    # calculate the absorption of a dataset given the transmission
    def calculateAbsorption(self, transmission):
        absorption = (np.log10(transmission)) * -1
        
        return absorption
    
    # calculate a linear function to defer the samples concentration from
    def calculateConcentration(self, concentrations, absorptions):
        
        absorptions = np.asarray(absorptions)
        absorptions  = [np.mean(i) for i in absorptions]
        
        fit = np.polyfit(concentrations, absorptions, 1)
        xs = list(range(1, 200))
        ys = [Tools.polynomialOne(fit, i) for i in xs]  
        
        result =  Tools.wrap(self, xs,ys)
        return result
        
        
        
