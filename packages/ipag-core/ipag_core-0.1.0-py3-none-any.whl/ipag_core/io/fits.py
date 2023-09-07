from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from astropy.io import fits
from ipag_core.define import DataProcessor, DataReader, DataWriter, MetadataLike ,  DataTuple, PathGetter
from ipag_core.io.array import array_loop 
from ipag_core.path import Path 
from ipag_core.log import get_logger

import numpy as np 

log = get_logger()


def parse_meta_value( value ):
    """ Some conversion value for fits header """
    if isinstance( value, datetime):
        return str(value)
    return value 


def metadata2header( metadata: MetadataLike, model:fits.Header | None )->fits.Header:
    """ convert some metadata object into a fits header """
    if isinstance(metadata, fits.Header ):
        return metadata
    if metadata is None:
        metadata = {} 

    if model is None:
        return fits.Header( metadata )
     
    header = model.copy()
    if hasattr( metadata, "keys"):
        for key in metadata.keys():
            header[key] = parse_meta_value (metadata[key])
    else:
        for key, value in metadata:
            header[key] = parse_meta_value( value )
    return header

@dataclass
class FitsDataIo(DataReader, DataWriter):
    """ Fits file reader 

    Parameters:
        file: file name, absolute or relative path 
        path: default is Path(".") curent directory 
        overwrite: if True (default) file is overwriten 
        extention: fits extention number or name 
        header_model: optional, a fits.Header object containing default 
            fits file header to write. Values are updated from metadata 
            to a model copy.
    """
    file: str 
    path: Path = field(default_factory=Path)
    overwrite: bool = True
    extension: int | str = 0
    header_model: fits.Header | None = None 
    
    def write_data(self, data: Any, metadata: MetadataLike | None = None):
        """ Write data into fits file  """
        filename = self.path.get_path(self.file)
        
        fits.writeto(
                 filename, data, 
                 header=metadata2header(metadata, self.header_model),
                 overwrite=self.overwrite
            )
        log.info(f"Data file '{filename}' writen")

    def read_data(self)->DataTuple:
        filename = self.path.get_path(self.file)
        with fits.open( filename ) as fh_list:
            fh = fh_list[self.extension]
            return DataTuple(fh.data.copy(), fh.header)


@dataclass
class FitsFilesArrayDataReader(DataReader):
    """ Fits DataReader IO using a list of fits file

    Fits file data are merged into one single array     
    The metadata (header) of individual file is lost 
    """
    files: list[str]
    path: PathGetter = field(default_factory=Path)
    extension: int = 0
    
    def read_data(self):
        files = (self.path.get_path(file) for file in self.files) 
        data = [] 
        header = {}
        for i, file in enumerate(files):
            data.append( fits.getdata(file, self.extension) )
            header[f'file{i}'] = file
        data = np.asarray(data)
        return DataTuple(data, header) 


class FitsFileLooperDataIo(DataReader):
    """ Loop over a list of fits file and return file data at each read 
    When the list is over it will restart from begining

    Attributes:
        files: list of fits files to loop on 
        path: Path object to resolve file path 
        extension: extension number or name from which data and metadata is extracted
    """
    files: list[str]
    path: PathGetter = field(default_factory=Path)
    extension: int = 0

    _iteration = 0
       
    def read_data(self)->DataTuple:
        index = self._iteration%len(self.files)
        file = self.files[index]
        path = self.path.get_path(file)
        data = fits.getdata( path, self.extension)
        header = {'file':file, 'iteration':self._iteration}
        self._iteration += 1 
        return DataTuple(data, header) 

class FitsArrayLooperDataReader(DataReader):
    """ DataReader that read a fits file and loop over a given axis 

    Attributes:
        file: fits file name 
        path: path object to resolve file path
        extension: exetension number or name for which data is extracted 
        cash: If True (default) file raw data is cashed. 
            If False the data is red at each read_data() call 
        axis: int the array axis to loop on 
    """
    file: str 
    path: PathGetter = field(default_factory=Path)
    extension: int | str = 0

    cash: bool = True 
    axis: int = 0 

    _iteration = 0
    _data_cash = None
    
    def _read_raw_data(self):
        path = self.path.get_path(self.file)
        return fits.getdata(path, self.extension)  

    def _get_raw_data(self):
        if self.cash:
            if self._data_cash is None:
                self._data_cash = self._read_raw_data() 
            return self._data_cash 
        return self._read_raw_data()    

    def read_data(self)->DataTuple:
        raw_data = self._get_raw_data()         
        data = array_loop( raw_data, self._iteration, axis=self.axis)
        metadata = {'iteration':self._iteration}
        self._iteration += 1
        return DataTuple( data, metadata )


if __name__ == "__main__":
    FitsDataIo("test")

