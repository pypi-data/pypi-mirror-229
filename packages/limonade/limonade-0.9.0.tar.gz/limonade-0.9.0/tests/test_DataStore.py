import pytest
# import numpy as np
# from types import SimpleNamespace
import sys
# sys.path.append('../src')
sys.path.append('src')
from limonade import data
from data_for_tests import *


# ================================= Dummy data =============================
# data is two energy channel data with an event every second. Second channel
# is slower. There is one coincident event. The data is divided into three separate parts to be loaded.
@pytest.fixture()
def emptydata1():
    return empty_data


@pytest.fixture()
def lonedata1():
    return dummy_data1


@pytest.fixture()
def multidata1():
    return dummy_multidata1


@pytest.fixture()
def multidata2():
    return dummy_multidata2


@pytest.fixture()
def multidata3():
    return dummy_multidata3

# @pytest.fixture()
# def d_store_small_block():
#     return data.DataStore('time', block_size=5)


# @pytest.fixture()
# def d_store_big_block():
#     return data.DataStore('time', block_size=1000000)


# ================================= initialization =========================
def test_empty():
    ds = data.DataStore('time', block_size=1000000)
    assert ds.size == 0
    assert ds.num_evt == 0
    assert ds.max_t == 0


@pytest.mark.xfail
def test_empty_get():
    # d_store_big_block.get(0, 'energy')
    ds = data.DataStore('time', block_size=1000000)
    ds.get(0, 'energy')


@pytest.mark.xfail
def test_empty_get_block(d_store_big_block):
    # d_store_big_block.get_block(0, 1000)
    ds = data.DataStore('time', block_size=1000000)
    ds.get_block(0, 1000)


@pytest.mark.parametrize("block_size", [5, 100])
def test_lonedata(lonedata1, block_size):
    #d_store_small_block.add(lonedata1, t_offset=0)
    ds = data.DataStore('time', block_size)
    ds.add(lonedata1, t_offset=0)
    assert ds.size == 1
    assert ds.num_evt == 14
    assert ds.max_t == 14000000000


'''
def test_lonedata_big(lonedata1):
    #d_store_big_block.add(lonedata1, t_offset=0)
    ds = data.DataStore('time', block_size=1000000)
    ds.add(lonedata1, t_offset=0)
    assert ds.size == 1
    assert ds.num_evt == 14
    assert ds.max_t == 14000000000
'''
@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata(multidata1, multidata2, multidata3, block_size):
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    assert ds.size == 3
    assert ds.num_evt == 14
    assert ds.max_t == 14000000000


@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata_with_offset(multidata1, multidata2, multidata3, block_size):
    """
    Same as previous, but add a one-second time offset to second and third data

    """
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=1000000000)
    ds.add(multidata3, t_offset=1000000000)
    assert ds.size == 3
    assert ds.num_evt == 14
    assert ds.max_t == 16000000000


# Test cases for get_block (single file case):
# 1: start and stop within a block
# 2: start in beginning of block and stop within a block
# 3: start within a block and stop at end of block
# 4: start in beginning of block and stop at end of block
# 5: start at beginning of block and stop outside data

@pytest.mark.xfail
def test_lonedata_1_wrong_block(lonedata1):
    ds = data.DataStore('time', block_size=5)
    # d_store_small_block.add(lonedata1, t_offset=0)
    ds.add(lonedata1, t_offset=0)
    # we have bloc_size of 5
    ds.get_block(1, 7)


@pytest.mark.parametrize("block_size", [5, 100])
def test_lonedata_1(lonedata1, block_size):
    ds = data.DataStore('time', block_size)
    ds.add(lonedata1, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(1, 6)
    assert data_block['time'][0] == 2000000000
    assert data_block['time'][-1] == 6000000000
    assert data_block['energy'][0, 0] == 102
    assert data_block['energy'][-1, 1] == 502


@pytest.mark.parametrize("block_size", [5, 100])
def test_lonedata_2(lonedata1, block_size):
    # 2: start in beginning of block and stop within a block
    ds = data.DataStore('time', block_size)
    ds.add(lonedata1, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(0, 5)
    print(data_block)
    assert data_block['time'][0] == 1000000000
    assert data_block['time'][-1] == 5000000000
    assert data_block['energy'][0, 0] == 101
    assert data_block['energy'][-1, 0] == 104


@pytest.mark.parametrize("block_size", [5, 100])
def test_lonedata_3(lonedata1, block_size):
    # 3: start within a block and stop at end of block
    ds = data.DataStore('time', block_size)
    ds.add(lonedata1, t_offset=0)
    data_block = ds.get_block(9, 14)
    assert data_block['time'][0] == 10000000000
    assert data_block['time'][-1] == 14000000000
    assert data_block['energy'][0, 0] == 108
    assert data_block['energy'][-1, 0] == 112
    assert data_block['energy'][-1, 1] == -1


@pytest.mark.parametrize("block_size", [14, 100])
def test_lonedata_4(lonedata1, block_size):
    # 4: start in beginning of file and stop at end of file
    ds = data.DataStore('time', block_size)
    ds.add(lonedata1, t_offset=0)
    data_block = ds.get_block(0, 14)
    assert data_block['time'][0] == 1000000000
    assert data_block['time'][-1] == 14000000000
    assert data_block['energy'][0, 0] == 101
    assert data_block['energy'][-1, 0] == 112
    assert data_block['energy'][-1, 1] == -1


@pytest.mark.parametrize("block_size", [20, 100])
def test_lonedata_5(lonedata1, block_size):
    # 5: start at beginning of file and stop outside data
    ds = data.DataStore('time', block_size)
    ds.add(lonedata1, t_offset=0)
    # we have block_size of 5
    data_block = ds.get_block(0, 20)
    assert data_block['time'][0] == 1000000000
    assert data_block['time'][-1] == 14000000000
    assert data_block['energy'][0, 0] == 101
    assert data_block['energy'][-1, 0] == 112
    assert data_block['energy'][-1, 1] == -1


# Test cases for get_block (multi-file, single file case):
# 1: start and stop within a file
# 2: start in beginning of file and stop within a file
# 3: start within a file and stop at end of file
# 4: start in beginning of file and stop at end of file
# 5: start at beginning of file and stop outside data

@pytest.mark.parametrize("block_size", [4, 100])
def test_multidata_single1(multidata1, multidata2, multidata3, block_size):
    # 1: start and stop within a block
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have block_size of 4 to fit in a block
    data_block = ds.get_block(1, 5)
    assert data_block['time'][0] == 2000000000
    assert data_block['time'][-1] == 5000000000
    assert data_block['energy'][0, 0] == 102
    assert data_block['energy'][-1, 0] == 104


@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata_single2(multidata1, multidata2, multidata3, block_size):
    # 2: start in beginning of file and stop within a file
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(0, 5)
    assert data_block['time'][0] == 1000000000
    assert data_block['time'][-1] == 5000000000
    assert data_block['energy'][0, 0] == 101
    # assert data_block['energy'][-1, 1] == 502


@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata_single3(multidata1, multidata2, multidata3, block_size):
    # 3: start within a file and stop at end of file
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(1, 6)

    assert data_block['time'][0] == 2000000000
    assert data_block['time'][-1] == 6000000000
    assert data_block['energy'][0, 0] == 102
    assert data_block['energy'][-1, 1] == 502


@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata_singlea4(multidata1, multidata2, multidata3, block_size):
    # a4: start in beginning of first file and stop at end of file
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(1, 6)
    print(data_block)
    assert data_block['time'][0] == 2000000000
    assert data_block['time'][-1] == 6000000000
    assert data_block['energy'][0, 0] == 102


@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata_singleb4(multidata1, multidata2, multidata3, block_size):
    # b4: start in beginning of later file and stop at end of file
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(6, 11)
    print(data_block)
    assert data_block['time'][0] == 7000000000
    assert data_block['time'][-1] == 11000000000
    assert data_block['energy'][0, 0] == 106
    #assert data_block['energy'][-1, 1] == 502


@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata_single5(multidata1, multidata2, multidata3, block_size):
    # 4: start in beginning of file and stop at end of file
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have block_size of 5
    data_block = ds.get_block(11, 16)
    assert data_block['time'][0] == 12000000000
    assert data_block['time'][-1] == 14000000000
    assert data_block['energy'][0, 0] == 110
    assert data_block['energy'][-1, 0] == 112


# Test cases for get_block (multi-file, multi file case):
# 1: start and stop within a file
# 2: start in beginning of file and stop within a block
# 3: start within a file and stop at end of file
# 4: start in beginning of file and stop at end of file
# 5: start at beginning of file and stop outside data
# 6: start in previous file and stop at first event of last file

@pytest.mark.parametrize("block_size", [10, 100])
def test_multidata_multi1(multidata1, multidata2, multidata3, block_size):
    # Start and stop within a block. Jump through one file.
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have block_size of 5
    data_block = ds.get_block(2, 12)
    print(data_block)
    assert data_block['time'][0] == 3000000000
    assert data_block['time'][-1] == 12000000000
    assert data_block['energy'][0, 1] == 501
    assert data_block['energy'][-1, 0] == 110

@pytest.mark.parametrize("block_size", [9, 100])
def test_multidata_multi2(multidata1, multidata2, multidata3, block_size):
    # 2: start in beginning of first file and stop within a block
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(0, 9)
    assert data_block['time'][0] == 1000000000
    assert data_block['time'][-1] == 9000000000
    assert data_block['energy'][0, 0] == 101
    assert data_block['energy'][-1, 1] == 503


@pytest.mark.parametrize("block_size", [5, 100])
def test_multidata_multi3(multidata1, multidata2, multidata3, block_size):
    # 3: start in middle of second file and stop to end of third file
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(9, 14)
    assert data_block['time'][0] == 10000000000
    assert data_block['time'][-1] == 14000000000
    assert data_block['energy'][0, 0] == 108
    assert data_block['energy'][-1, 0] == 112


@pytest.mark.parametrize("block_size", [8, 100])
def test_multidata_multi4(multidata1, multidata2, multidata3, block_size):
    # 4: start in beginning of file and stop at end of file
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(6, 14)
    assert data_block['time'][0] == 7000000000
    assert data_block['time'][-1] == 14000000000
    assert data_block['energy'][0, 0] == 106
    assert data_block['energy'][-1, 0] == 112


@pytest.mark.parametrize("block_size", [10, 100])
def test_multidata_multi5(multidata1, multidata2, multidata3, block_size):
    # 5: start at beginning of file and stop outside data
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(6, 16)
    assert data_block['time'][0] == 7000000000
    assert data_block['time'][-1] == 14000000000
    assert data_block['energy'][0, 0] == 106
    assert data_block['energy'][-1, 0] == 112

@pytest.mark.parametrize("block_size", [18, 100])
def test_multidata6_first_event_of_last_block(multidata1, multidata2, multidata3, block_size):
    # Start in previous block and stop at first event of last block. A special case due to silly
    # way _get_idx works.
    ds = data.DataStore('time', block_size)
    ds.add(multidata1, t_offset=0)
    ds.add(multidata2, t_offset=0)
    ds.add(multidata3, t_offset=0)
    # we have bloc_size of 5
    data_block = ds.get_block(7, 12)

    assert data_block['time'][0] == 8000000000
    assert data_block['time'][-1] == 12000000000
    assert data_block['energy'][0, 0] == 107
    assert data_block['energy'][-1, 0] == 110

# 5: start at beginning of block and stop outside data





