# class Person:
#     def __init__(self):
#         self.name = "A"
#         self.age = 5
    
#     @classmethod
#     def fly(lsc, a):
#         print("正在执行！", lsc)
#         lsc.name = 1
#         print(lsc.name) 
        
#         print(a)

import pandas as pd 
import math
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller as adf 
from statsmodels.stats.diagnostic import acorr_ljungbox as lbtest
from statsmodels.tsa.arima.model import ARIMA


# df = pd.read_csv("./EX.csv")
tsdata = df
tsdata["Year"] = pd.to_datetime(tsdata["Year"], format="%Y")
tsdata.index = tsdata["Year"]
del tsdata["Year"]

training = tsdata.truncate(after='2004-1-1')
testing = tsdata.truncate(before='2005-1-1')
plot_acf(training, lags=12)
test = adf(training, autolag="AIC")
print("P-value = {}".format(test[1]) )


if __name__ == "__main__":
    a = Person()
    a.fly(2)
    f = "./test.log"
    t = open(f, "r") 