from __future__ import annotations
from typing import Any, Union, NamedTuple
from typing_extensions import Protocol, runtime_checkable
from abc import abstractmethod



class MetadataLike(Protocol):
    def __getitem__(self, item):
        """ header keys should be accessisble """
    def __setitem__(self, item , value):
        """ header keys should be updatable """
    
    def copy(self):
        """ Header must copy itself """


class DataTuple(NamedTuple):
    """ Named tuple holding data and metadata """
    data: Any 
    metadata: MetadataLike
    def __array__(self):
        return self.data 


class DataContainerProtocol(Protocol):
    data: Any
    metadata: MetadataLike
    
    def get_data(self):
        """ Should have a get_data method """

@runtime_checkable
class DataProcessor(Protocol):
    """ Protocol. a DataProcessor must have this defined  methodd  """
    def process_data(self, data, metadata=None)->Any:
        """ process data and return new data """

@runtime_checkable
class PathGetter(Protocol):
    """ Protocol. A PathGetter object must define these methods 
    
    The role of a PathGetter is to resolve an absolute path from 
    a relative file name. 
    """
    def get_directory(self)->str:
        """ must return the directory """

    def get_path(self, file: str)->str:
        """ must return a resolved complete path from a file path """

@runtime_checkable
class DataReaderAndWriter(Protocol):
    def write_data(self, data, header=None):
        """ A Io can write data """
        
    def read_data(self)->tuple[Any, MetadataLike]:
        """ An Io can read """

@runtime_checkable
class DataReader(Protocol):
    """ Protocol. The role of a DataReader is to read data and metadata from any source """
    @abstractmethod
    def read_data(self)->DataTuple:
        """ Read data and return in a DataTuple(data, metadata) """ 
        ... 

@runtime_checkable
class DataWriter(Protocol):
    """Protocol. A DataWriter write date and metadata to any target (file, plots, device, ...) """
    @abstractmethod
    def write_data(self, data: Any, metadata: MetadataLike | None = None)->None:
        """ Write data and optional metadata """
        ...


@runtime_checkable
class SuportsSetup(Protocol):
    """ An object dedicated to the setup of something, like a device """
    @abstractmethod
    def setup(self, obj: Any):
        """ run the setup """

@runtime_checkable
class SupportsUpdate(Protocol):
    """ An object dedicted to update a current state """
    @abstractmethod
    def update(self, obj: Any):
        """ update to self any real state """
