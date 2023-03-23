import ast
import copy
from typing import Iterable, List, cast

class Marker(ast.NodeTransformer):
    """Mark the target statement."""
    def __init__(self, line_no: int) -> None:
        super().__init__()

        self.line_no = line_no
        self.found = False          # target found?
        self.loop_level = 0         # depth of loop (0 indicates outside loop body)
        self.is_first_stmt = False  # is the first stmt in block?

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(node, ast.stmt) and node.lineno == self.line_no:
            setattr(node, '__target__', (self.loop_level > 0, self.is_first_stmt))
            self.found = True
            return node
        # TODO: YOUR CODE HERE
        # The following is the super class implementation. Modify it to maintain
        # `self.loop_level` and `self.is_first_stmt` correctly.
        self.is_first_stmt = False
        if isinstance(node, ast.While)  or isinstance(node, ast.For):
            self.loop_level=self.loop_level+1
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                self.is_first_stmt=True
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)           
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        if isinstance(node, ast.While) or isinstance(node, ast.For):
            self.loop_level=self.loop_level-1
        return node


def mk_abstract() -> ast.expr:
    """Create an AST for the abstract condition."""
    return ast.Name('__abstract__')

class MutationOperator(ast.NodeTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.mutated = False

class Tighten(MutationOperator):
    """If the target statement is an if-statement, transform its condition by
    conjoining an abstract condition: if c => if c and not __abstract__."""
    # TODO: YOUR CODE HERE
    def generic_visit(self, node):
        if self.mutated:
            return node
        if isinstance(node,ast.If) and hasattr(node,'__target__'):
            if isinstance(node.test, list):
                test = ast.BoolOp(ast.And(),node.test + ast.UnaryOp(ast.Not(),mk_abstract()))
            else:
                test = ast.BoolOp(ast.And(),[node.test, ast.UnaryOp(ast.Not(),mk_abstract())])
            node.test=test
            self.mutated=True
            return node      

        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
    pass


class Loosen(MutationOperator):
    """If the target statement is an if-statement, transform its condition by
    disjoining an abstract condition: if c => if c or __abstract__."""
    # TODO: YOUR CODE HERE
    def generic_visit(self, node):
        if self.mutated:
            return node
        if isinstance(node,ast.If) and hasattr(node,'__target__'):
            if isinstance(node.test, list):
                test = ast.BoolOp(ast.Or(),node.test + mk_abstract())
            else:
                test = ast.BoolOp(ast.Or(),[node.test, mk_abstract()])
            node.test=test
            self.mutated=True
            return node      

        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
    pass


class Guard(MutationOperator):
    """Transform the target statement so that it executes only if an abstract condition is false:
    s => if not __abstract__: s."""
    # TODO: YOUR CODE HERE
    def generic_visit(self, node):
        if self.mutated:
            return node
        if hasattr(node,'__target__'):
            new_node = ast.If()
            new_node.body=[node]
            new_node.orelse=[]
            new_node.test=ast.UnaryOp(ast.Not(),mk_abstract())
            self.mutated=True
            return new_node      

        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
    pass


class Break(MutationOperator):
    """If the target statement is in loop body, right before it insert a `break` statement that
    executes only if an abstract condition is true, i.e., if __abstract__: break."""
    def __init__(self, required_position: bool) -> None:
        """If `required_position` is `True`, this operation is performed only when the 
        target is the first statement.
        If `required_position` is `False`, this operation is performed only when the 
        target is not the first statement.
        """
        super().__init__()
        self.required_position = required_position

    # TODO: YOUR CODE HERE
    def generic_visit(self, node):
        if self.mutated:
            return node
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        if hasattr(value,'__target__'):
                            if value.__target__[0] and value.__target__[1] == self.required_position:        
                                new_node = ast.If()
                                new_node.body =[ast.Break()]
                                new_node.test=mk_abstract()
                                new_node.orelse=[]
                                new_values.append(new_node)
                                self.mutated=True
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node


class Mutator:
    """Perform program mutation."""
    def __init__(self, tree: ast.Module, line_no: int, log: bool = False) -> None:
        assert isinstance(tree, ast.Module)
        self.old_tree = tree
        self.log = log
        
        marker = Marker(line_no)
        self.marked_tree = marker.visit(copy.deepcopy(tree))
        assert marker.found

    def apply(self, ops: List[MutationOperator] = None) -> Iterable[ast.Module]:
        if ops is None:
            # in default priority order
            ops = [Tighten(), Loosen(), Break(True), Guard(), Break(False)] 

        for visitor in ops:
            new_tree = visitor.visit(copy.deepcopy(self.marked_tree))
            if self.log:
                print(f'-> {visitor.__class__.__name__}', '✓' if visitor.mutated else '✗')

            if visitor.mutated:
                if self.log:
                    print(ast.unparse(new_tree))

                yield new_tree
