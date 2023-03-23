from inspect import getsourcelines
import sys
from types import CodeType
from debuggingbook.Debugger import Debugger

class CallInfo:
    def __init__(self, caller: CodeType, line_no: int) -> None:
        #print("init")
        self.caller = caller
        self.loc = line_no

    def __repr__(self) -> str:
        #print("repr")
        head = f'File "{self.caller.co_filename}", line {self.loc}, in {self.caller.co_name}'
        lines, start = getsourcelines(self.caller)
        code = lines[self.loc - start].strip()
        return f'{head}\n  {code}'

class Debugger(Debugger):
    def __init__(self, *, file = sys.stdout) -> None:
        self.finish : bool =False
        self.finish_func = None
        self.next : bool =False
        self.next_func = None
        super().__init__(file=file)
    def break_command(self,arg: str="") -> None:
        """Set a breakpoint in given line. If no line is given, list all breakpoints"""
        
        if arg:
            try:
                x=int(arg)
                source_lines, line_number = \
                    getsourcelines(self.frame.f_code)
                if x in range(len(source_lines)+line_number):
                    self.breakpoints.add(x)
                else:
                    print(f"Line number {arg} out of bond ({line_number} - {len(source_lines)+line_number-1})") #TODO
            except ValueError:
                print(f"Expect a line number, but found '{arg}'")        
        self.log("Breakpoints:", self.breakpoints)
    def delete_command(self, arg: str = "") -> None:
            """Delete a breakpoint from the set of breakpoints"""
            try:
                x=int(arg)
                try:
                    self.breakpoints.remove(x)
                except KeyError:
                    self.log(f"No such breakpoint: {x}")
                
            except ValueError:
                print(f"Expect a line number, but found '{arg}'")
            self.log("Breakpoints:", self.breakpoints)
    def assign_command(self, arg: str) -> None:
        """Use as 'assign VAR=VALUE'. Assign VALUE to local variable VAR."""
        
        sep = arg.find('=')
        if sep > 0:
            var = arg[:sep].strip()
            expr = arg[sep + 1:].strip()
        else:
            self.help_command("assign")
            return

        vars = self.local_vars
        if not var.isidentifier():
            self.log(f"SyntaxError: '{var}' is not an identifier")
            return
        if var not in vars:
            self.log(f"Warning: a new variable '{var}' is created")
        try:
            vars[var] = eval(expr, self.frame.f_globals, vars)
        except Exception as err:
            self.log(f"{err.__class__.__name__}: {err}")
    
    def next_command(self, arg: str) -> None:
        """Resume the execution until the next line in this file"""
        self.next_func=self.frame.f_back
        self.next=True
        self.continue_command()
        
    def where_command(self,arg:str) -> None:
        """Print the stack trace."""
        print("Traceback (most recent call last):")
        f=self.frame
        list_of_tracebacks=[]
        while f.f_back is not None:
                list_of_tracebacks.append(f)                
                f=f.f_back
        #del list_of_tracebacks[-1]
        for i in reversed(list_of_tracebacks):
            print(CallInfo(i.f_code ,i.f_lineno))
        
    def finish_command(self,arg:str) -> None:
        """Resume execution until the current function returns."""
        self.finish=True
        self.finish_func=self.frame
        self.continue_command()
        
        
        
    def stop_here(self) -> bool:
        """Function expanded with commands next and finish """
        if(self.finish and self.event=="return" and self.frame==self.finish_func): 
            self.finish=False
            self.finish_func=None
            return True
        if(self.next and self.frame.f_back==self.next_func):
            self.next=False
            self.next_func=None
            return True
        return super().stop_here()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No input file", file=sys.stderr)
        exit(1)

    module_name = sys.argv[1][:-3] # remove .py
    exec(f"from {module_name} import debug_main")

    with Debugger():
        debug_main()
