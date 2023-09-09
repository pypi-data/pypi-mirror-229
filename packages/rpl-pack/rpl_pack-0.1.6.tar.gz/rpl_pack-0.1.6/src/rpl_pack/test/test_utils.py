
import pytest
import numpy as np

from rpl_pack.utils import make_array


# make_array()
def test_make_array_num_to_array():
    assert make_array(1.).all() == np.array([1.]).all()

def test_make_array_tuple_to_array():
    assert make_array((1.,)).all() == np.array([1.]).all()

def test_make_array_list_to_array():
    assert make_array([1., 2., 3.]).all() == np.array([1., 2., 3.]).all()

def test_make_array_array_to_array():
    assert make_array(np.array([1., 2., 3.])).all() == np.array([1., 2., 3.]).all()

