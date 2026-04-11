import numpy as np

def extract_thermal_features(data):
    return {
        "mean_temp": float(np.mean(data)),
        "max_temp": float(np.max(data))
    }