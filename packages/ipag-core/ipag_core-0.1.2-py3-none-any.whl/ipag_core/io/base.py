from __future__ import annotations
from dataclasses import dataclass, field

from ipag_core.define import DataReader, DataWriter, DataProcessor, DataTuple
from ipag_core.processor import data_processor


def _get_read_method( obj ):
    if hasattr(obj, "read_data"):
        return  obj.read_data 
    if hasattr(obj, "__call__"):
        return  obj 
    raise ValueError("input io must have a read_data() method or shall be callable")     

def _get_write_method( objs ):
    wrfuncs = []
    for io in objs:
        if hasattr(io, "write_data"):
            wrfuncs.append(io.write_data)
        elif hasattr(io, "__call__"):
            wrfuncs.append( io ) 
        else:
            raise ValueError("outputio must have a write_data() method or shall be callable")

    def write(data, metadata=None):
        for wr in wrfuncs:
            wr( data, metadata)
    return write 
    

@dataclass
class PipeDataIo(DataReader, DataWriter):
    """ Merge one 'input' io and one or more 'output' io 

    Args:
        io_in: A single io object or a callable with signature f() called at read
        *io_outs: A list of io object or functions with signature f(data,metadata). 
            They are executed with the same order when write method is called 

    Note the read and write function are built at init. Therefore the input and output 
    io(s) cannot be change after object creation. 
    """
    def __init__(self, io_in, *io_outs):
        self.read_data  = _get_read_method(io_in) 
        self.write_data = _get_write_method( io_outs)
    
    def read_data(self):
        raise ValueError("PipeIo wasn't initialised")

    def write_data(self, data, metadata = None):
        raise ValueError("PipeIo wasn't initialised")

class ProcessedDataIo(DataReader, DataWriter):
    """ An Io Processing data before returning it 

    Args:
        io: The Io object use to first retrieve the data 
        *procs: list of processor. can be 
            - a Process object 
            - a callable with signature  f(data) 
            - a list of one of these three types

    Exemple:
        
        import numpy as np 
        from ipag_core.ipag import ProcessedIo, FitsIo, procfunc 
        
        image_io = ProcessedIo( FitsIo("my_cube.fits"), procfunc(np.mean, axis=0) )
        data, metdata = image_io.read()     

    """
    def __init__(self, io: DataReader | DataWriter, *procs: DataProcessor):
        self.io = io 
        self.proc = data_processor(procs) 
    
    def write_data(self, data, metadata=None):
        self.io.write_data( data, metadata )

    def read_data(self):
        data, metadata = self.io.read_data() 
        data = self.proc.process_data( data, metadata)
        return DataTuple( data, metadata )



