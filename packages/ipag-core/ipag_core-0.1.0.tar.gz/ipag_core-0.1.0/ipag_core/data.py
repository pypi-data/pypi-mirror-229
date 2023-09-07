from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import numpy as np 
from ipag_core.define import DataReader, DataWriter,  MetadataLike  

@dataclass
class DataContainer:
    """ Data & Metadata Container 

    The load method is used as an update of the data and metadata

    Atributes:
        data: Any object representing the data 
        metadata: dictionary like object 
        io: a DataIo object used by load method 
        onload: a List of callable with signature f(data, metadata)
            All function will be called when a load() as been success-full.

    """
    data: Any | None = None  
    metadata: MetadataLike = field(default_factory=dict)
    io: DataReader| DataWriter | None = None 
    onload: list[Callable]  = field(default_factory=list) 

    def load(self, io: DataReader = None):
        """ load data and metadata internaly 
        
        Args:
            io (DataIo, optional): the io used to read data & metadata 
                If not given the object io attribute is used. If no io is defined 
                Exception is raise. 
        """
        io = io or self.io 
        if io is None:
            raise ValueError("This data container has no default io, provide one")
        if not isinstance( io, DataReader):
            raise IOError( "Io is not readable. Cannot read data" )
        
        data, metadata = io.read_data() 
        self.data = data  
        self.metadata = metadata 
        for callback in self.onload:
            callback( data, metadata)
    
    def save(self, io: DataWriter = None):
        """ write internal data and metadata
        
        Args:
            io (DataIo, optional): the io used to write data & metadata 
                If not given the object io attribute is used. If no io is defined 
                Exception is raise. 
        """
        io = io or self.io 
        if io is None:
            raise ValueError("This data container has no default io, provide one")
        if not isinstance( io, DataWriter):
            raise IOError( "Io is not writable. Cannot save data" )

        io.write_data( self.data, self.metadata)

    def __array__(self):
        return self.data 
    


# TODO: move this zelda speciffic stuff 
def _dp(index):
    return property( lambda self: self.data[0][index])

class Centering(DataContainer):
    """ Data with property of centering information """
    current_x_0_cred = _dp(0)
    current_y_0_cred = _dp(1)
    current_x_0_slm  = _dp(2)
    current_y_0_slm  = _dp(3)
    current_theta    = _dp(5)
    current_grand_x  = _dp(6)
    current_grand_y  = _dp(7)



