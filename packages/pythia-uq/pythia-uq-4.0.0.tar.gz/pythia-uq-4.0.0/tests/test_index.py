"""
File: tests/test_index.py
Author: Nando Hegemann
Gitlab: https://gitlab.com/Nando-Hegemann
Description: Test pythia.index module.
SPDX-License-Identifier: LGPL-3.0-or-later OR Hippocratic-3.0-ECO-MEDIA-MIL
"""
import numpy as np
from pythia import index


def test_IndexSet() -> None:
    """Test Multiindex class."""
    indices = np.array([[0, 1], [0, 0], [1, 1], [0, 0], [2, 0]], dtype=int)
    index_set = index.IndexSet(indices)

    # test get_sobol_tuple_list()
    expected = [(1,), (2,), (1, 2)]
    val = index_set.sobol_tuples
    assert len(expected) == len(val)
    assert np.all([np.all(left == right) for left, right in zip(expected, val)])

    # test get_index_number()
    val = index_set.get_index_number(np.array([[2, 0], [0, 0]]))
    expected = np.array([3, 0], dtype=int)
    assert np.all(val == expected)
    assert np.all(index_set.indices[val] == np.array([[2, 0], [0, 0]]))

    # test get_sobol_tuple_number()
    val = index_set.get_sobol_tuple_number([(1,), (1, 2)])
    assert np.all(val == [0, 2])

    # test index_to_sobol_tuple()
    val = index_set.index_to_sobol_tuple(indices)
    expected = [(2,), (), (1, 2), (), (1,)]
    assert len(val) == len(expected)
    assert np.all([np.all(left == right) for left, right in zip(expected, val)])

    # test sobol_tuple_to_indices()
    val = index_set.sobol_tuple_to_indices([(1,), (1, 2)])
    expected = [np.array([[2, 0]], dtype=int), np.array([[1, 1]], dtype=int)]
    assert np.all([np.all(v == e) for v, e in zip(val, expected)])


def test_sort_index_array() -> None:
    """Test sort_index_array."""
    indices = np.array([[0, 1], [0, 0], [1, 1], [0, 0], [2, 0]], dtype=int)
    expected = np.array([[0, 0], [0, 1], [1, 1], [2, 0]], dtype=int)
    assert np.all(index.sort_index_array(indices) == expected)

    indices = np.array([], dtype=int)
    expected = np.array([], dtype=int)
    assert np.all(index.sort_index_array(indices) == expected)


def test_union() -> None:
    """Test union."""
    indices_1 = np.array([[0, 0], [1, 0], [2, 0]], dtype=int)
    indices_2 = np.array([[0, 0], [0, 1], [0, 2]], dtype=int)
    indices_3 = np.array([[0, 5]], dtype=int)
    expected = np.array([[0, 0], [0, 1], [1, 0], [0, 2], [2, 0], [0, 5]], dtype=int)
    assert np.all(index.union([indices_1, indices_2, indices_3]) == expected)


def test_intersection() -> None:
    """Test intersection."""
    indices_1 = np.array([[0, 0], [1, 0], [2, 0]], dtype=int)
    indices_2 = np.array([[0, 1], [0, 2], [2, 0], [0, 0]], dtype=int)
    indices_3 = np.array([[0, 0]], dtype=int)
    indices_4 = np.array([[0, 5]], dtype=int)

    expected = indices_1
    assert np.all(index.intersection([indices_1]) == expected)

    expected = np.array([[0, 0], [2, 0]], dtype=int)
    assert np.all(index.intersection([indices_1, indices_2]) == expected)

    expected = np.array([[0, 0]], dtype=int)
    assert np.all(index.intersection([indices_1, indices_2, indices_3]) == expected)

    expected = np.array([], dtype=int)
    assert np.all(index.intersection([indices_1, indices_2, indices_4]) == expected)


def test_set_difference() -> None:
    """Test set_difference."""
    indices = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=int)
    subtract = np.array([[1, 0], [2, 0]], dtype=int)
    expected = np.array([[0, 0], [0, 1], [1, 1]], dtype=int)
    val = index.set_difference(indices, subtract)
    assert np.all(val == expected)


def test_tensor_set() -> None:
    """Test tensor_set."""
    lower = [0, 1]
    shape = [3, 3]
    expected = np.array([[0, 1], [0, 2], [1, 1], [1, 2], [2, 1], [2, 2]], dtype=int)
    assert np.all(index.tensor_set(shape, lower) == expected)

    shape = [1, 4, 2]
    lower = [0, 0, 1]
    expected = np.array([[0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 3, 1]], dtype=int)
    assert np.all(index.tensor_set(shape, lower) == expected)


def test_lq_bound_set() -> None:
    """Test lq_bound_set."""
    val = index.lq_bound_set([3, 3], 2, 1)
    expected = np.array([[0, 0], [0, 1], [1, 0], [0, 2], [1, 1], [2, 0]], dtype=int)
    assert np.all(val == expected)

    val = index.lq_bound_set([3, 2], 2, 1)
    expected = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [2, 0]], dtype=int)
    assert np.all(val == expected)

    val = index.lq_bound_set([3, 3], 2, 0.1)
    expected = np.array([[0, 0], [0, 1], [1, 0], [0, 2], [2, 0]], dtype=int)
    assert np.all(val == expected)

    val = index.lq_bound_set([3, 3], 2, 100)
    expected = np.array(
        [[0, 0], [0, 1], [1, 0], [0, 2], [1, 1], [2, 0], [1, 2], [2, 1], [2, 2]],
        dtype=int,
    )
    assert np.all(val == expected)


def test_simplex_set() -> None:
    """Test simplex_set."""
    val = index.simplex_set(2, 2)
    expected = np.array([[0, 0], [0, 1], [1, 0], [0, 2], [1, 1], [2, 0]], dtype=int)
    assert np.all(val == expected)

    val = index.simplex_set(3, 1)
    expected = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0]], dtype=int)
    assert np.all(val == expected)


if __name__ == "__main__":
    test_intersection()
