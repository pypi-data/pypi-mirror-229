import pytest
# import numpy as np
# from types import SimpleNamespace
import sys
from limonade import data
from data_for_tests import *
sys.path.append('../src')
sys.path.append('src')


class DummyDataForTcache:
    """
    Dummy data class that has the correct interface for TimeCache. This implements the minimum possible interface. Its
    size is a measure of the interdependency of Data class and TimeCache.
    """
    def __init__(self, index_data, data_dict):
        # set interface used by TimeCache
        self.data = data_dict
        self.num_ch = self.data['energy'].shape[1]  # take num_ch from data, needed by TimeCache.__init__
        self.index_data = index_data
        self._data_store = SimpleNamespace(num_evt=data_dict[index_data].shape[0])

    def get_data(self, var_name, index, index2=None):
        """
        get_data is called by TimeCache._slice_timing
        :param var_name:
        :param index:
        :param index2:
        :return:
        """
        if index2 is None:
            return self.data[var_name][index, ...]
        else:
            return self.data[var_name][index:index2, ...]

    def get_end_time(self):
        """
        get_end_time is called by TimeCache.get_total_time
        :return:
        """
        return self.data[self.index_data][-1]


# ================================= Dummy data =============================
# data1 is two energy channel data with an event every second. Second channel
# is slower. There is one coincident event.

dummy_dtype_1ch = np.dtype([('idx', '<u8'), ('t', '<u8'), ('dt0', '<f4')])
dummy_dtype_2ch = np.dtype([('idx', '<u8'), ('t', '<u8'), ('dt0', '<f4'), ('dt1', '<f4')])
dummy_empty_timing_1ch = np.zeros((1,), dtype=dummy_dtype_1ch)
dummy_empty_timing_2ch = np.zeros((1,), dtype=dummy_dtype_2ch)

# A case of malformed timing. Only one channel in the timing
dummy_timing_1ch = np.zeros((1,), dtype=dummy_dtype_1ch)
dummy_timing_1ch[0] = (dummy_data1['time'].shape[0],
                       dummy_data1['time'][-1],
                       (dummy_data1['energy'][:, 0] >= 0).sum() * 8000e-9)

# Next case is how the timing is supposed to be: single channel per row (online) unless by accident hitting
# the same event (in the end of data for example). The data is partitioned to 4-event updates, with the slow
# channel having only 3 events.
# Timing gives both channels with separate lines. The timing is written for every daq update (every n events or for
# every delta t) plus once in the end of data (per channel).
# The event parser is responsible for producing correct timing data.
dummy_timing_2ch = np.zeros((4,), dtype=dummy_dtype_2ch)
dummy_timing_2ch[0] = (4,
                       dummy_data1['time'][4],
                       (dummy_data1['energy'][:4 + 1, 0] >= 0).sum() * 8000e-9,
                       0.0)
dummy_timing_2ch[1] = (8,
                       dummy_data1['time'][8],
                       0.0,
                       (dummy_data1['energy'][:8 + 1, 1] >= 0).sum() * 4000e-9)
dummy_timing_2ch[2] = (9,
                       dummy_data1['time'][9],
                       (dummy_data1['energy'][4 + 1:9 + 1, 0] >= 0).sum() * 8000e-9,
                       0.0)
dummy_timing_2ch[3] = (13,
                       dummy_data1['time'][13],
                       (dummy_data1['energy'][9 + 1:, 0] >= 0).sum() * 8000e-9,
                       0.0)


@pytest.fixture()
def t_cache_empty():
    return data.TimeCache(DummyDataForTcache('time', empty_data))


@pytest.fixture()
def t_cache_ready():
    cache = data.TimeCache(DummyDataForTcache('time', dummy_data1))
    cache.set(np.concatenate((dummy_empty_timing_2ch, dummy_timing_2ch)))
    return cache


@pytest.fixture()
def test_data_1():
    return dummy_data1


@pytest.fixture()
def timing_case_1ch():
    return dummy_timing_1ch


@pytest.fixture()
def timing_case1():
    return dummy_timing_2ch


# ================================= initialization =========================
def test_empty_idx(t_cache_empty):
    assert t_cache_empty.timing.dtype[0] == np.dtype('uint64')


def test_empty_time(t_cache_empty):
    assert t_cache_empty.timing.dtype[1] == np.dtype('uint64')


def test_empty_dt(t_cache_empty):
    assert t_cache_empty.timing.dtype[2] == np.dtype('float32')


def test_empty_num_fields(t_cache_empty):
    assert len(t_cache_empty.timing.dtype) == t_cache_empty.parent.num_ch + 2


# ================================= set timing =========================
@pytest.mark.xfail
def test_set_malformed_timing(t_cache_empty, timing_case_1ch):
    # should fail on setting 1 ch timing on 2ch data
    t_cache_empty.set(dummy_timing_1ch)


@pytest.mark.xfail
def test_set_incomplete_timing(t_cache_empty, timing_case1):
    # should fail on setting data with no zeroes in the beginning
    t_cache_empty.set(timing_case1)


def test_set_timing(t_cache_empty, timing_case1):
    t_cache_empty.set(np.concatenate((dummy_empty_timing_2ch, timing_case1)))
    assert np.all(t_cache_empty.timing[1:] == timing_case1)


# ================================= find =========================
@pytest.mark.parametrize("test_input,expected", [((np.uint64(0), np.uint64(2e9)), (0, 1)),
                                                 ((np.uint64(0), np.uint64(9.5e9)), (0, 3)),
                                                 ((np.uint64(5.5e9), np.uint64(11.5e9)), (1, 4)),
                                                 ((np.uint64(9.5e9), np.uint64(15.5e9)), (2, 4)),
                                                 ((np.uint64(15.5e9), np.uint64(15.6e9)), (4, 4))])
# ("2+4", 6), pytest.param("6*9", 42, marks=pytest.mark.xfail)],)
def test_find_timing(t_cache_ready, test_input, expected):
    res = t_cache_ready.find(test_input)
    assert np.all([res[x] == expected[x] for x in range(2)])


@pytest.mark.parametrize("test_input,expected", [((np.uint64(0), np.uint64(2e9)), (0, 1)),
                                                 ((np.uint64(0), np.uint64(9.5e9)), (0, 3)),
                                                 ((np.uint64(5.5e9), np.uint64(11.5e9)), (1, 4)),
                                                 ((np.uint64(9.5e9), np.uint64(15.5e9)), (1, 4)),
                                                 ((np.uint64(5e9), np.uint64(10e9)), (1, 3))])
def test_find_timing_ch0(t_cache_ready, test_input, expected):
    res = t_cache_ready.find(test_input, 0)
    assert np.all([res[x] == expected[x] for x in range(2)])


@pytest.mark.parametrize("test_input,expected", [((np.uint64(0), np.uint64(2e9)), (0, 2)),
                                                 ((np.uint64(0), np.uint64(9.5e9)), (0, 2)),
                                                 ((np.uint64(5.5e9), np.uint64(11.5e9)), (0, 2)),
                                                 ((np.uint64(9.5e9), np.uint64(15.5e9)), (2, 2)),
                                                 ((np.uint64(0), np.uint64(9e9)), (0, 2))])
def test_find_timing_ch1(t_cache_ready, test_input, expected):
    print(t_cache_ready.timing)
    res = t_cache_ready.find(test_input, 1)
    print(res, expected)
    assert np.all([res[x] == expected[x] for x in range(2)])


# ================================= get timing =========================
def test_get_full_timing(t_cache_ready, timing_case1):
    assert np.all(t_cache_ready.get_timing()[1:] == timing_case1)


def test_get_partial_start_aligned(t_cache_ready, timing_case1):
    timing = t_cache_ready.get_timing((0, 8.5e9))

    print('got')
    print(timing)
    print('should be')
    target = np.zeros((3,), dtype=timing.dtype)
    target['idx'] = np.array((0, 4, 7))
    target['t'] = np.array((0, 5e9, 8e9))
    target['dt0'] = np.array((0, 3.2e-5, 3.2e-5/(10-5)*(8.5-5)))
    target['dt1'] = np.array((0, 0, 1.2e-5/9*8.5))
    print(target)
    assert timing[0] == dummy_empty_timing_2ch
    assert np.all(timing == target)


def test_get_partial_ch0_aligned(t_cache_ready, timing_case1):
    timing = t_cache_ready.get_timing((5e9, 10e9))
    # assert timing[0] == dummy_empty_timing_2ch
    print('got')
    print(timing)
    print('should be')
    target = np.zeros((3,), dtype=timing.dtype)
    target['idx'] = np.array((4, 8, 9))
    target['t'] = np.array((5e9, 9e9, 10e9))
    target['dt0'] = np.array((0, 0, 3.2e-5))
    target['dt1'] = np.array((0, 1.2e-5/9*(9-5), 0))
    print(target)

    assert np.all(timing == target)


def test_get_partial_ch1_nodata(t_cache_ready, timing_case1):
    timing = t_cache_ready.get_timing((11e9, 13.1e9))
    # assert timing[0] == dummy_empty_timing_2ch
    print('got')
    print(timing)
    print('should be')
    target = np.zeros((2,), dtype=timing.dtype)
    target['idx'] = np.array((10, 12))
    target['t'] = np.array((11e9, 13e9))
    target['dt0'] = np.array((0., 8.0e-6*2.1))
    target['dt1'] = np.array([0., 0.])
    print(target)
    assert np.all(timing == target)


def test_get_partial_end_incl_ch1_nodata(t_cache_ready, timing_case1):
    timing = t_cache_ready.get_timing((11e9, 12e9))
    # assert timing[0] == dummy_empty_timing_2ch
    print('got')
    print(timing)
    print('should be')
    target = np.zeros((2,), dtype=timing.dtype)
    target['idx'] = np.array((10, 11))
    target['t'] = np.array((11e9, 12e9))
    target['dt0'] = np.array((0., 8.0e-6))
    target['dt1'] = np.array([0., 0.])
    print(target)

    assert np.all(timing == target)


def test_get_partial_single_ch1_nodata(t_cache_ready, timing_case1):
    timing = t_cache_ready.get_timing((11e9, 11.5e9))
    # assert timing[0] == dummy_empty_timing_2ch
    print('got')
    print(timing)
    print('should be')
    target = np.zeros((1,), dtype=timing.dtype)
    target['idx'] = np.array((10,))
    target['t'] = np.array((11e9,))
    target['dt0'] = np.array((4.0e-6,))
    target['dt1'] = np.array([0.])
    print(target)

    assert np.all(timing == target)


'''
def test_get_partial_interpolated(t_cache_ready, timing_case1):
    timing = t_cache_ready.get_timing((0, 8e9))
    assert timing[0] == dummy_empty_timing_2ch
    print('got')
    print(timing[1:])
    print('should be')
    print(timing_case1[:3])
    timing[1:] == timing_case1[:3]
    assert np.all(timing[1:] == timing_case1[:3])


# ================================= join timing =========================
#def test_add_timing(t_cache_empty, timing_case1):
#    t_cache_empty.set(np.concatenate((dummy_empty_timing_2ch, timing_case1)))
#    assert np.all(t_cache_empty.get_timing()[1:] == timing_case1)
'''