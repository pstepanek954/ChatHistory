import pandas as pd
import numpy as np


tmp = {1: [1,2], 5:[3,4]}
t = pd.DataFrame({"A":[1,2,3,4], "B" : np.array([1,2,3,4]), "C" : np.array([1,2,3,4]) + np.array([1,2,3,4])})
print(t)