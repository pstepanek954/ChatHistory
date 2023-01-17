class Person:
    def __init__(self):
        self.name = "A"
        self.age = 5
    
    @classmethod
    def fly(lsc, a):
        print("正在执行！", lsc)
        lsc.name = 1
        print(lsc.name) 
        
        print(a)
if __name__ == "__main__":
    a = Person()
    a.fly(2)