from debuggingbook.StatisticalDebugger import Collector
from types import FrameType
from typing import Any, Dict
import inspect

from predicate import Predicate

def ackermann(m, n):
    if m == 0:
        return n + 1
    elif n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))


class PredicateCollector(Collector):
    
    def __init__(self) -> None:
        super().__init__()
        self.predicates: Dict[str, Predicate] = dict()
    
    def collect(self, frame: FrameType, event: str, arg: Any) -> None:
        if event!='call':
            return
        dic=inspect.getargvalues(frame).locals
        name = frame.f_code.co_name
        for var in dic.keys():
            values=dic.copy()
            values['0']=0
            values.pop(var)
            for v in values.keys():                
                eq=name+f'({var} == {v})'
                if dic[var]==values[v]:
                    p = Predicate(eq,true=1, observed=1)
                else:
                    p = Predicate(eq,true=0, observed=1)
                self.predicates[eq]=p
                greater=name+f'({var} > {v})'
                if dic[var]>values[v]:
                    p = Predicate(greater,true=1, observed=1)
                else:
                    p = Predicate(greater,true=0, observed=1)
                self.predicates[greater]=p
                smaller=name+f'({var} < {v})'
                if dic[var]<values[v]:
                    p = Predicate(smaller,true=1, observed=1)
                else:
                    p = Predicate(smaller,true=0, observed=1)
                self.predicates[smaller]=p
        return
        #pass
        # TODO: implement
        
        
def test_collection():
    with PredicateCollector() as pc:
        ackermann(0, 1)
    results = {
        'ackermann(m == 0)': (1, 1),
        'ackermann(m < 0)': (0, 1),
        'ackermann(m > 0)': (0, 1),
        'ackermann(m < n)':  (1, 1),
        'ackermann(m > n)':  (0, 1),
        'ackermann(n == 0)': (0, 1),
        'ackermann(n < 0)': (0, 1),
        'ackermann(n > 0)': (1, 1),
        'ackermann(n < m)':  (0, 1),
        'ackermann(n > m)':  (1, 1),
        'ackermann(m == n)': (0, 1),
        'ackermann(n == m)': (0, 1),
    }
    for pred in results:
        pred = pc.predicates[pred]
        p, o = results[pred.rpr]
        assert pred.true == p, f'True for {pred} was wrong, expected {p}, was {pred.true}' 
        assert pred.observed == o, f'Observed for {pred} was wrong, expected {o}, was {pred.observed}' 
        assert pred.failing_observed == pred.successful_observed == pred.failing_true == pred.successful_true == 0

        
if __name__ == '__main__':
    test_collection()
    print('Successful')
