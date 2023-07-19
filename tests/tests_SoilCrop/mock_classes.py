"""
RUFAS: Ruminant Farm Systems Model
File name: mock_classes.py
Description: This file contains functions that create mock classes, using arguments to set attributes
Author(s): Clay Morrow, morrowcj@outlook.com
           Brandon DeBoer, brdeboer@wisc.edu
"""


from RUFAS.routines.field.crop.crop_types import base_crop
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.classes import Weather,Time
from unittest.mock import MagicMock


def mock_crop(dict=None, **kwargs):
    """
    Description:
        creates a BaseCrop mock object, with attributes set via function arguments
    Args:
        dict: an optional dictionary of attributes and values to set in the mock
        kwargs: attributes of the mock object. The argument name corresponds to the attribute name
        and the parameter value corresponds to the attribute value.
    Return:
         a mock of the BaseCrop class
    Example:
          `mock_crop(fr_root=0.38, biomass_actual=4.6)` creates a mock object with two attributes
          `fr_root` and `biomass_actual`, which equal 0.38 and 4.6 respectively.
          Identically: `mock_crop(dict = {"fr_root":0.38, "biomass_actual":4.6})`
    """

    if dict is not None:
        attrs = dict
    else:
        attrs = kwargs

    mcrop = MagicMock(base_crop.BaseCrop)

    for key, val in attrs.items():
        setattr(mcrop, key, val)

    return mcrop




def mock_soil(dict=None, **kwargs):
    """
    Description:
        creates a Soil mock object, with attributes set via function arguments
    Args:
        dict: an optional dictionary of attributes and values to set in the mock
        kwargs: attributes of the mock object. The argument name corresponds to the attribute name
        and the parameter value corresponds to the attribute value.
    Return:
         a mock of the Soil class
    Example:
          
    """

    if dict is not None:
        attrs = dict
    else:
        attrs = kwargs

    msoil = MagicMock(Soil)

    for key, val in attrs.items():
        setattr(msoil, key, val)

    return msoil


def mock_soil_layer(dict = None, **kwargs):
    """
    Description:
        creates a SoilLayer mock object, with attributes set via function arguments
    Args:
        dict: an optional dictionary of attributes and values to set in the mock
        kwargs: attributes of the mock object. The argument name corresponds to the attribute name
        and the parameter value corresponds to the attribute value.
    Return:
         a mock of the SoilLayer class
    Example:
          
    """

    if dict is not None:
        attrs = dict
    else:
        attrs = kwargs
    
    msoil_layer = MagicMock(Soil.SoilLayer)

    for key, val in attrs.items():
        setattr(msoil_layer,key,val)

    return msoil_layer

def mock_weather(dict = None, **kwargs):
    """
    Description:
        creates a Weather mock object, with attributes set via function arguments
    Args:
        dict: an optional dictionary of attributes and values to set in the mock
        kwargs: attributes of the mock object. The argument name corresponds to the attribute name
        and the parameter value corresponds to the attribute value.
    Return:
         a mock of the Weather class
    Example:
          
    """
    
    if dict is not None:
        attrs = dict
    else:
        attrs = kwargs
    
    mweather = MagicMock(Weather)

    for key,val in attrs.items():
        setattr(mweather,key,val)

    return mweather

def mock_time(dict = None, **kwargs):
    """
    Description:
        creates a Time mock object, with attributes set via function arguments
    Args:
        dict: an optional dictionary of attributes and values to set in the mock
        kwargs: attributes of the mock object. The argument name corresponds to the attribute name
        and the parameter value corresponds to the attribute value.
    Return:
         a mock of the Time class
    Example:
          
    """

    if dict is not None:
        attrs = dict
    else:
        attrs = kwargs
    
    mtime = MagicMock(Time)

    for key,val in attrs.items():
        setattr(mtime,key,val)

    return mtime


