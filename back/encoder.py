import json
import numpy as np
import scipy as stats
import pandas as pd

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)



def encodeArray(array):
    
    return result

def encodeString(string):
    
    return result