from debugger import PerformanceDebugger, HitCollector
from examples import ex_1, ex_2, ex_3, ex_4,ex_5, ex_6
import random
def test_func(func, _range:int)->None:
    count=0
    over_input:int=None
    for i in range(_range):
        rd=random.randint(-100,100)
        with PerformanceDebugger(HitCollector) as pd:
            func(rd)
        if pd.is_overflow()==True:
            count+=1
            over_input=rd
    print(f"Function ended with {float(count/_range)} percent overflow\nExample of invalid input: {over_input}")
def test_func3(func, _range:int)->int:
    count=0
    over_input=None
    for i in range(_range):
        rd=random.randint(-100,100)
        rd2=random.randint(-100,100)        
        with PerformanceDebugger(HitCollector) as pd:
            func(rd,rd2)
        if pd.is_overflow()==True:
            count+=1
            over_input=tuple((rd,rd2))
    print(f"Function ended with {float(count/_range)} percent overflow\nExample of invalid input: {over_input}")
    print (pd)
if __name__=="__main__":
    # _range=100
    # print("ex1")
    # test_func(ex_1,_range)
    # print("ex2")
    # test_func(ex_2,_range)
    # print("ex3")
    # test_func3(ex_3,_range)
    # print("ex4")
    # test_func(ex_4,_range)
    # print("ex5")
    # test_func(ex_5,_range)
    # print("ex6")
    # test_func(ex_6,_range)
    with PerformanceDebugger(HitCollector) as pd:
           ex_5(-1)
    assert pd.is_overflow()
    print(pd)   