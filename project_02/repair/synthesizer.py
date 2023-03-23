import ast
import copy
import itertools
from types import CodeType
from typing import Any, Dict, List, Tuple
from repair.tester import *

class Template:
    """Condition template."""
    def __init__(self, meta_vars: List[Tuple[str, str]], body: ast.expr) -> None:
        self.args: List[str] = [s for s, _ in meta_vars]
        self.types: List[str] = [t for _, t in meta_vars]
        self.body = body

    @classmethod
    def from_lambda(cls, expr: str):
        """Parse a template from a string, basic syntax:
        (<var> : <type>, <var> : <type>, ...) => <condition>
        The lhs parenthesis is optional."""
        lhs, body = expr.split('=>')
        lhs = lhs.strip()
        if lhs.startswith('(') and lhs.endswith(')'):
            lhs = lhs[1:-1]
        lhs = lhs.split(',') if ',' in lhs else [lhs]

        meta_vars = []
        for x in lhs:
            arg, typ = x.split(':')
            meta_vars.append( (arg.strip(), typ.strip()) )
        
        body = ast.parse(body.strip()).body[0].value
        assert isinstance(body, ast.expr)
        return cls(meta_vars, body)

    def instantiate(self, vars: List[str]) -> ast.expr:
        """Instantiate a template with `vars`. Just like applying values to lambda expressions."""
        assert len(vars) == len(self.args)
        return self.NameTransformer(dict(zip(self.args, vars))).visit(copy.deepcopy(self.body))

    class NameTransformer(ast.NodeTransformer):
        def __init__(self, mapping: Dict[str, str]) -> None:
            super().__init__()
            self.mapping = mapping

        def visit_Name(self, node: ast.Name) -> ast.Name:
            if node.id in self.mapping:
                node.id = self.mapping[node.id]
                return node

            return node

class Synthesizer:
    """Condition synthesis."""

    def __init__(self, tree: ast.Module, pos_tests: List[CodeType], neg_tests: List[CodeType],
                 k: int = 10, extra_templates: List[Template] = None, log: bool = False) -> None:
        self.abstract_tree = tree
        self.pos_tests = pos_tests
        self.neg_tests = neg_tests
        self.k = k
        self.extra_templates = extra_templates
        self.log = print if log else no_log

        self.condition: ast.expr            # synthesized condition
        self.concrete_tree: ast.Module      # instantiated tree
    
    def apply(self) -> bool:
        """Entry point."""
        overall_record = Record([], [])

        for test_code in self.neg_tests:
            self.log(f'--> Execute {test_code.co_name}')

            success, record = exec_abstract(self.abstract_tree, test_code, iter([]))
            self.log(f'--(0/{self.k})->', '✓' if success else '✗', record.values)

            i = 1
            while not success and i <= self.k:
                if i == self.k: # the last attempt
                    future_values = all_true()
                else:
                    future_values = iter(self.flip(record.values))

                success, record = exec_abstract(self.abstract_tree, test_code, future_values)
                self.log(f'--({i}/{self.k})->', '✓' if success else '✗', record.values)
                i += 1

            if success:
                overall_record += record
            else:
                return False # synthesis failed

        for test_code in self.pos_tests:
            self.log(f'--> Execute {test_code.co_name} (+)')

            success, record = exec_abstract(self.abstract_tree, test_code, iter([]))
            self.log('   ', '✓' if success else '✗', record.values)
            
            assert success
            overall_record += record
        
        if self.solve(overall_record):
            self.concrete_tree = Instantiate(self.condition).visit(
                copy.deepcopy(self.abstract_tree))
            return True
        else:
            return False

    def flip(self, values: List[bool]) -> List[bool]:
        """Flip the last `False` to `True`, and drop all the `True`s after the last `False`."""
        # TODO: YOUR CODE HERE
        while len(values)!=0 and values[-1]:
            values.pop()
        if len(values) == 0:
            return []
        else:
            values[-1]=True
        return values

    def solve(self, constraints: Record) -> bool:
        """Solve constraints. Returns if a solution is found. Set `self.condition` when found."""
        # TODO: YOUR CODE HERE
        #print(constraints)
        for env in constraints.envs:
            for key in env:
                ops=[ast.Eq(),ast.NotEq()]                
                for op in ops:                    
                    candidate = ast.Compare(left=ast.Name(key,ast.Load()),ops=[op],comparators=[ast.Constant(value=env[key])])
                    #print(ast.dump(candidate))
                    if self.sat(candidate,constraints):
                        self.condition=candidate
                        return True
        if self.extra_templates is None:
            return False
        for template in self.extra_templates:
            # print(template.types)
            candidate={}
            for index,ty in enumerate(template.types):
                for env in constraints.envs:
                    for key in env:
                        if type(env[key]).__name__ == ty:
                            if index in candidate:
                                if not key in candidate[index]:
                                    candidate[index].append(key)
                            else:
                                candidate[index]=[key]
            possible_perms=1
            maximal=[]
            actual=[]
            for key in candidate:
                possible_perms=possible_perms*len(candidate[key])
                maximal.append(len(candidate[key]))
                actual.append(0)
            # print(candidate)
            # print(possible_perms)
            for i in range(possible_perms):
                c=[]
                for i in candidate:
                   c.append(candidate[i][actual[i]]) 
                c=template.instantiate(c)
                if self.sat(c,constraints):
                    self.condition=c
                    return True
                actual[0]=actual[0]+1
                for index in range(len(actual)-1):
                    if actual[index] == maximal[index]:
                        actual[index]=0
                        actual[index+1]=actual[index+1]+1         
        return False
                 
    def sat(self, cond: ast.expr, constraints: Record) -> bool:
        """Check if `cond` satisfies the `constraints`."""
        for env, value in zip(constraints.envs, constraints.values):
            try:
                actual = eval(ast.unparse(cond), {}, env)
            except Exception:
                return False

            if actual != value:
                return False

        return True
    
    def validate(self) -> bool:
        """Check correctness of the repaired program `self.concrete_tree`."""
        return run_tests(self.concrete_tree, self.neg_tests + self.pos_tests)

def no_log(self, *values: object) -> None:
    pass

