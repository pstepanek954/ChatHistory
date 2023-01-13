import pandas as pd
import numpy as np

class Person:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __str__(self):
        fmt = "The a is {} , b is {}"
        return fmt.format(self.a , self.b)


a = Person("Nan", "Naaaa")

print(a)