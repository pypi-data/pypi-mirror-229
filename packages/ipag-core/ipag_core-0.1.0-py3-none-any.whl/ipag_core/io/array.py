from __future__ import annotations
from typing import Callable
from dataclasses import dataclass, field 
import numpy as np

from ipag_core.define import DataTuple, DataWriter, DataReader



def array_loop( a:np.ndarray, index: int, axis: int =0):
    l = a.shape[axis]
    return np.take( a, index%l , axis)


@dataclass
class ArrayLooperDataReader(DataReader):
    """ A :class:`DataReader` looping over the given axis of an array 

    Attributes:
        array: input array 
        axis:  which axis the array is looped 
        metadata: some default metadata copied at each read 
    """
    array: np.ndarray 
    axis: int = 0
    metadata: dict = field( default_factory=dict)
    #--------------------------------------------
    _iteration = 0 

    def read_data(self):
        data = array_loop( self.data, self._iteration, self.axis)
        metadata = {**{'iteration':self._iteration}, **self.metadata}
        self._iteration += 1
        return DataTuple(data, metadata)


# The folowing are mostly for simulators 

@dataclass
class RandomDataReader(DataReader):
    """ A generating Random Data 
    
    Attributes:
        loc:  "mean", center of the distribution
        scale: Standard deviation (spread or "width") of the distribution
        shape: Output shape 
        generator: cllable taking the 3 above argument (e.g. np.random.normal)
    """
    loc: float = 0.0
    scale: float = 1.0 
    shape: tuple[int] = tuple()
    generator: Callable = np.random.normal 

    def read_data(self)->DataTuple:
        return DataTuple( 
            self.generator( self.loc,  self.scale, self.shape), 
            {'loc':self.loc, 
             'scale': self.scale, 
             'distrib': getattr(self.generator, "__name__", "unknown")
            } 
        )

@dataclass 
class _ArrayIo(DataReader):
    shape: tuple 
    dtype: type = np.float64 
    creator: Callable = np.ndarray

    def read_data(self)->DataTuple:
        return DataTuple( self.creator(self.shape, self.dtype), {} )

@dataclass 
class OnesDataReader(_ArrayIo):
    """ A DataReader returning array filles with ones """
    creator: Callable = np.ones 

@dataclass 
class ZerosDataReader(_ArrayIo):
    """ A DataReader returning array filles with zeros """
    creator: Callable = np.zeros 


