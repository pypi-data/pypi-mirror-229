""" This is the public API for the ipag_core package """

from ipag_core.log import init_logger, get_logger

from ipag_core.define import (
    DataProcessor,
    DataReader, 
    DataTuple,
    DataWriter, 
    PathGetter,
    MetadataLike
)

from ipag_core.io.base import (
    ProcessedDataIo, 
    PipeDataIo, 
)

from ipag_core.io.fits import (
    FitsDataIo,
    FitsFilesArrayDataReader, 
    FitsFileLooperDataIo,
    FitsArrayLooperDataReader, 
)

from ipag_core.io.array import (
    ArrayLooperDataReader, RandomDataReader, OnesDataReader, ZerosDataReader
)

from ipag_core.data import( 
    DataContainer
)

from ipag_core.log import ( 
    init_logger, 
    get_logger,
)

from ipag_core.processor import (
    data_processor, 
    ProcessChain, 
    DataReducer, 
    DarkSubstractor, 
)

from ipag_core.path import (
    Path, 
    AutoPath, 
    UniquePath, 
    TodayPath, 
    ResourcePath
)

#place holder of an IPAG configured BaseModel 
from ipag_core.pydantic import (
    BaseModel,
    Field, 
    RootModel, 
    UserModel, 
    StateModel, 
    user_model_config
)

