from __future__ import annotations
from dataclasses import dataclass, field
from functools import partial
from inspect import signature
from typing import Any, Callable
from typing_extensions import Protocol

import numpy as np
from ipag_core.define import DataProcessor, DataContainerProtocol, DataTuple


def data_processor(obj)->DataProcessor:
    """ parse input to a processor 
    
    Accepted input are: 
        - A Processor, returned as it is 
        - A Callable with signature `f(data)` , encapsulated in a FuncProc 
        - An iterable containing a valid processor input, encapsulated in a ProcessChain 

    Exemple:
        from functools import partial 

        processor( np.squeeze )
        processor( partial(np.mean, axis=0) )
        # equivalent to : 
        procfunc( np.mean, axis=0) 

        processor( [ procfunc(np.mean, axis=0), lambda x: x-256] ) 
        
    """
    if isinstance(obj, DataProcessor):
        return obj 
    if hasattr(obj, "__call__"):
        return FuncProc( obj )
    if hasattr( obj, "__iter__"):
        return ProcessChain( *(data_processor(child) for child in obj) )
    raise ValueError(f"{type(obj)} is not a processor")


def procfunc(func, *args, **kwargs):
    return FuncProc( partial(func, *args, **kwargs))

@dataclass
class FuncProc:
    """ Simple data process to encapsulate any function `f(data)` as process 

    see proc func 
    """
    func: Callable
    def process_data(self, data, metadata=None):
        return self.func(data)


class ProcessChain:
    """ Processor using  several processor and execute them in cascade """
    def __init__(self, *processors):
        self.processors = [data_processor(proc) for proc in processors]
    
    def process_data(self, data, metadata=None):
        for proc in self.processors:
            data = proc.process_data(data, metadata)
        return data

def _default_reducer():
    return np.mean 
    
@dataclass 
class DataReducer:
    """ Reduce data with a function f(data, axis=) as e.g. np.mean 

    Parameters:
        reducer: reduce function, default is np.mean 
        axis: axis number to reduce 'a la numpy'  
    """
    
    reducer: Callable = field( default_factory= _default_reducer )# method to collapse the first cube dimension 
    """ method of signature f(a, axis=) to reduce the data. Default is np.mean  """
    
    axis: int | tuple = 0 
    """ Which axis is being reduced """

    def process_data(self, data, metadata=None):
        return self.reducer(np.asarray(data), axis=self.axis)

@dataclass 
class DarkSubstractor:
    """ Processor substracted a Dark to data """
    dark: DataTuple | float | np.ndarray 
    
    def process_data(self, data, metadata=None):
        return np.asarray(data)-np.asarray(self.dark)


