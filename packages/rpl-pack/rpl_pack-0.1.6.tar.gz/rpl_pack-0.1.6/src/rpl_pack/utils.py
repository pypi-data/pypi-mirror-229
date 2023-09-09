"""
Utility classes and functions mostly for internal use.

"""


import time
import json
from typing import Any, Callable

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """Subclass of json.JSONEncoder used for encoding numpy arrays as json
    objects.
    """
    def default(self, obj: Any) -> Any:
        """Encode with numpy.ndarray.tolist() if numpy array, otherwise use
        json.JSONEncoder.default() encoding.
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def make_array(x: Any, dtype=None) -> np.ndarray:
    """Create numpy array from any native data type and/or data structure.
    Used to homogenize inputs to functions acting internally in RPL_WEB_PACK
    api.
    """
    return np.asarray(x, dtype) if isinstance(x, (list, tuple, set, np.ndarray)) \
            else np.array([x])


def encode_arrays(data_keys: list, data: list, dtype=None) -> str:
    """Encode numpy arrays as json objets using NumpyEncoder."""
    data_dict = {}
    for key, val in zip(data_keys, data):
        val_arr = make_array(val, dtype)
        data_dict[key] = val_arr
    json_dumps = json.dumps(data_dict, cls=NumpyEncoder)
    return json_dumps


def decode_arrays(data: Any, dtype=None) -> dict:
    """Decode json objects into numpy arrays."""
    if isinstance(data, (str, bytes, bytearray)):
        data = json.loads(data)
    for key, val in data.items():
        data[key] = make_array(val)
    return data


def timer(func: Callable) -> Callable:
    """Decorator to time a function."""
    def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        t0 = time.time()
        res = func(*args, **kwargs)
        print(f'Time to evaluate {func.__name__}(): {time.time() - t0} s')
        return res
    return wrapped_func


def scfstb_m3m3(value: float) -> float:
    """Convert from standard cubic feet (scf)/stock tank barrel (stb) to
    cubic meter (m3)/cubic meter (m3).
    """
    return 0.17811*value


def m3m3_scfstb(value: float) -> float:
    """Convert from from cubic meter (m3)/cubic meter (m3)
    standard cubic feet (scf)/stock tank barrel (stb).
    """
    return value/0.17811