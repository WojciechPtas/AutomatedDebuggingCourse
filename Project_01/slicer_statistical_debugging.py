import logging
import os
import pickle
import shutil
from ast import NodeTransformer, parse, unparse, With, withitem ,Name, If, Call, FunctionDef, Assign,Return, arg, arguments, expr, stmt, Load, Store, Attribute, Str,copy_location
from pathlib import Path
from types import FrameType
import typing
from typing import List, Any, Set, Dict, Tuple
import subprocess
from debuggingbook.StatisticalDebugger import ContinuousSpectrumDebugger, Collector, RankingDebugger
from debuggingbook.Slicer import Slicer
DependencyDict = Dict[
    str,
    Set[
        Tuple[
            Tuple[str, Tuple[str, int]],
            Tuple[Tuple[str, Tuple[str, int]], ...]
        ]
    ]
]


class Instrumenter(NodeTransformer):

    def instrument(self, source_directory: Path, dest_directory: Path, excluded_paths: List[Path], log=False) -> None:
        """
        TODO: implement this function, such that you get an input directory, instrument all python files that are
        TODO: in the source_directory whose prefix are not in excluded files and write them to the dest_directory.
        TODO: keep in mind that you need to copy the structure of the source directory.
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

        shutil.copy('lib.py', dest_directory / 'lib.py')
        #print(f"Copyin from {source_directory}")
        for directory, sub_directories, files in os.walk(source_directory):
            # Iterates directory and its subdirectories in the form of (directory, [sub_directories], [files])
            logging.info(f'Current dir: {directory}')
            logging.info(f'Current sub_dirs: {sub_directories}')
            logging.info(f'Current files: {files}')
            #print(f'Current dir: {directory}')
            #print(f'Current sub_dirs: {sub_directories}')
            #print(f'Current files: {files}')
            for d in sub_directories:
                #print(dest_directory / d)
                #print("dupa")
                os.makedirs(dest_directory/d)
                #print(f"Created subdir: {d}")
            for f in files:            
                a=directory.replace(str(source_directory),str(dest_directory))
                #print(a)
                shutil.copy2(directory +"//"+ f,a)
                if not Path(directory +"//"+ f) in excluded_paths:
                    file = open(a + "//" + f,"r+")
                    read_file=file.read()
                    file.close()
                    read_file="from lib import _data\n"+read_file
                    tree = parse(read_file)
                    s =Slicer(log=False)
                    transformed=s.transform(tree=tree)
                    file=open(a + "//" + f,"w")
                    file.write(unparse(transformed))
                    file.close()

class DependencyCollector(Collector):

    def __init__(self, dump_path: Path):
        super().__init__()
        self.dump_path = dump_path

    def traceit(self, frame: FrameType, event: str, arg: Any) -> None:
        pass  # deactivate tracing overall, not required.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.dump_path, 'rb') as dump:
            deps = pickle.load(dump)
        self.collect(deps)

    def collect(self, dependencies: DependencyDict):
        """
        TODO: Collect the dependencies in the specified format.
        :param dependencies: The dependencies for a run
        :return:
        """
        self.data=dependencies['data']
        self.control=dependencies['control']
        self.events_collected=set(self.data)
        self.events_collected.update(self.control)        
        #print(self.d)
    #pass

    def events(self) -> Set[Any]:
        
        return self.events_collected
           
       


class CoverageDependencyCollector(DependencyCollector):

    def events(self) -> Set[Any]:
        self.result=set()
        #print(len(self.events_collected))
        for event in self.events_collected:
            self.inspect(event)
        #print(self.result)
        return self.result
    def inspect(self, arg : Tuple) -> None:
        if len(arg)==2:
            if isinstance(arg[0], str) and isinstance(arg[1], int):
                self.result.add(arg)
                return
        for i in arg:
                if isinstance(i, Tuple):
                    self.inspect(i)
        return
class DependencyDebugger(ContinuousSpectrumDebugger, RankingDebugger):

    def __init__(self, coverage=False, log: bool = False):
        super().__init__(CoverageDependencyCollector if coverage else DependencyCollector, log)
        
        
if __name__ == "__main__":
    db = DependencyDebugger(coverage=True)
    os.chdir(Path('tmp'))
    with db.collect_pass(Path('dump')):
        subprocess.run(['python', '-m', 'unittest', 'test_middle.MiddleTests.test_123'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with db.collect_fail(Path("dump")):
        subprocess.run(['python', '-m', 'unittest', 'test_middle.MiddleTests.test_213'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    os.chdir(Path('..'))
    print(db.only_fail_events())
