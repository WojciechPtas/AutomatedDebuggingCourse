import logging
import os
import pickle
import shutil
import ast
from pathlib import Path
from types import FrameType
from typing import List, Any, Set, Tuple
from debuggingbook.Slicer import Slicer, TrackCallTransformer, TrackReturnTransformer, TrackParamsTransformer, TrackSetTransformer, TrackGetTransformer, TrackControlTransformer, DATA_TRACKER
from debuggingbook.StatisticalDebugger import ContinuousSpectrumDebugger, Collector, RankingDebugger

class InstrumentLinesParams(TrackParamsTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self.generic_visit(node)
        named_args = []
        for child in ast.iter_child_nodes(node.args):
            if isinstance(child, ast.arg):
                named_args.append(child)
        self.number_args=len(named_args)
        return super().visit_FunctionDef(node)
    def getNumArgs(self) -> int:
        return self.number_args
class InstrumentLinesControl(TrackControlTransformer):
    def __init__(self) -> None:
        self.locations=[]
        super().__init__()
    def make_with(self, block: List[ast.stmt]) -> List[ast.stmt]:
        """Create a subtree 'with _data: `block`'"""
        if len(block)==0:
            return []
        block_as_text = ast.unparse(block[0])
        if block_as_text.find('with ' + DATA_TRACKER)!=-1:
            return block  # Do not apply twice
        print(block[0].lineno)
        self.locations.append(block[0].lineno)       
        return super().make_with(block)
    def Getlocations(self)->List[int]:
        return self.locations
class InstrumentedSlicer(Slicer):
    def transformers(self) -> List[ast.NodeTransformer]:
        self.TC=InstrumentLinesControl()
        self.TP=InstrumentLinesParams()
        return [
            TrackCallTransformer(),
            TrackSetTransformer(),
            TrackGetTransformer(),
            self.TC,
            TrackReturnTransformer(),
            self.TP
        ]
    def transform(self, tree: ast.AST) -> ast.AST:
        tr=super().transform(tree)
        self.lines=[3]
        self.lines[0]+=self.TP.getNumArgs()
        self.lines.append(self.TC.Getlocations())
        return tr 
class Instrumenter(ast.NodeTransformer):

    def instrument(self, source_directory: Path, dest_directory: Path, excluded_paths: List[Path], log=False) -> None:
        """
        :param source_directory: the source directory where the files to instrument are located
        :param dest_directory:   the output directory to which to write the instrumented files
        :param excluded_paths:   the excluded path that should be skipped in the instrumentation
        :param log:              whether to log or not
        :return:
        """

        if log:
            logging.basicConfig(level=logging.INFO)

        assert source_directory.is_dir()

        if dest_directory.exists():
            shutil.rmtree(dest_directory)
        os.makedirs(dest_directory)

        shutil.copy('lib_fl.py', dest_directory / 'lib_fl.py')

        for directory, sub_directories, files in os.walk(source_directory):
            # Iterates directory and its subdirectories in the form of (directory, [sub_directories], [files])
            logging.info(f'Current dir: {directory}')
            logging.info(f'Current sub_dirs: {sub_directories}')
            logging.info(f'Current files: {files}')
            for d in sub_directories:
                os.makedirs(dest_directory/d)
            for f in files:            
                a=directory.replace(str(source_directory),str(dest_directory))
                #print(a)
                shutil.copy2(directory +"//"+ f,a)
                if not Path(directory +"//"+ f) in excluded_paths:
                    file = open(a + "//" + f,"r+")
                    read_file=file.read()
                    file.close()
                    
                    tree = ast.parse(read_file)
                    s = Slicer(log=False)
                    transformed=s.transform(tree=tree)
                    read_file=ast.unparse(transformed)
                    
                    file=open(a + "//" + f,"w")
                    file.write(read_file)
                    file.close()
                    
                    file=open(a + "//" + f,"r")
                    Lines = file.readlines()
                    count = 0
                    added_lines=[1,2,3]
                    for line in Lines:
                        count += 1
                        if line.find("with _data:")!=-1:
                            added_lines.append(count+3)
                        if line.find("_data.param")!=-1:
                            added_lines.append(count+3)
                    file.close()                            
                    read_file=f"from lib_fl import _data\nfrom lib_fl import lines\nlines.append({added_lines.__repr__()})\n"+ast.unparse(transformed)
                    #print(read_file)
                    file=open(a + "//" + f,"w")
                    file.write(read_file)
                    file.close()


class EventCollector(Collector):

    def __init__(self, dump_path: Path):
        super().__init__()
        self.dump_path = dump_path

    def traceit(self, frame: FrameType, event: str, arg: Any) -> None:
        pass  # deactivate tracing overall, not required.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.dump_path, 'rb') as dump:
            events = pickle.load(dump)
        self.collect(events)
            
    def collect(self, dependencies: Any):
        #print("Collecting!")
        self.data=dependencies['data']
        self.control=dependencies['control']
        self.lines=dependencies['lines']
        self.events_collected=set(self.data)
        self.events_collected.update(self.control)   

    def events(self) -> Set[Any]:
        self.result=set()
        #print(len(self.events_collected))
        for event in self.events_collected:
            self.inspect(event)
        self.res2=[]
        for i in self.result:
            a=list(i)
            l = [x for x in self.lines[0] if x <= a[1]]
            a[1] -= len(l)
            self.res2.append(tuple(a))
        #print(self.result)
        #print(self.res2)
        return self.res2
    def inspect(self, arg : Tuple) -> None:
        if len(arg)==2:
            if isinstance(arg[0], str) and isinstance(arg[1], int):
                self.result.add(arg)
                return
        for i in arg:
                if isinstance(i, Tuple):
                    self.inspect(i)
        return


class FaultLocalization(ContinuousSpectrumDebugger, RankingDebugger):

    def __init__(self, instrumenter: Instrumenter, log: bool = False):
        ContinuousSpectrumDebugger.__init__(self, collector_class=EventCollector, log=log)
        RankingDebugger.__init__(self, collector_class=EventCollector, log=log)
        
    def rank(self)->List[Tuple[str,int]]:
        def susp(event: Any) -> float:
            suspiciousness = self.suspiciousness(event)
            assert suspiciousness is not None
            return suspiciousness
        events = list(self.all_events())
        events.sort(key=susp, reverse=True)
        return events

if __name__=="__main__":
    print("main")