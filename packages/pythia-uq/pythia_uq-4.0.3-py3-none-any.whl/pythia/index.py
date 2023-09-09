"""
File: pythia/index.py
Author: Nando Hegemann
Gitlab: https://gitlab.com/Nando-Hegemann
Description: Create, manipulate and store information about multiindices.
SPDX-License-Identifier: LGPL-3.0-or-later OR Hippocratic-3.0-ECO-MEDIA-MIL
"""
import itertools
import numpy as np
import pythia as pt


class IndexSet:
    """Generate index set object for sparse PC expansion.

    A general polynomial chaos expansion of a function
    :math:`f\\colon\\Gamma\\subset\\mathbb{R}^M\\to\\mathbb{R}^J`
    with :math:`y\\sim\\pi` is given by

    .. math::
        f(y) = \\sum_{\\mu\\in\\mathbb{N}_0^M} \\mathbf{f}[\\mu]P_{\\mu}(y)
        \\quad\\mbox{for}\\quad
        \\mathbf{f}[\\mu] = \\int_\\Gamma f(y)P_\\mu(y)\\ \\mathrm{d}y,

    where :math:`\\mu` is a multiindex,
    :math:`\\mathbf{f}[\\mu]\\in\\mathbb{R}^J` is a coefficient vector and
    :math:`\\{P_\\mu\\}_{\\mu\\in\\mathbb{N}_0^M}` is an orthonormal basis in
    :math:`L^2(\\Gamma,\\pi)`.
    To approximate the infinite expansion choose an index set
    :math:`\\Lambda\\subset\\mathbb{N}_0^M` of multiindices and consider

    .. math::
        f(y) \\approx \\sum_{\\mu\\in\\Lambda} \\mathbf{f}[\\mu]P_{\\mu}(y),

    Parameters
    ----------
    indices : np.ndarray
        Array of multiindices with shape (#indices, param dim).

    Examples
    --------
    Create the sparse index set

    .. math::
        \\Lambda = \\{ (0,0), (1,0), (2,0), (0,1) \\} \\subset \\mathbb{N}_0^2

    >>> import pythia as pt
    >>> indices = np.array([[0, 0], [1, 0], [2, 0], [0, 1]], dtype=int)
    >>> index_set = pt.index.IndexSet(indices)
    """

    def __init__(self, indices: np.ndarray) -> None:
        """Initialize sparse multiindex object."""
        assert indices.ndim == 2 and indices.shape[0] > 0
        assert indices.dtype == int
        assert np.all(indices >= 0)
        self.indices = sort_index_array(indices)
        self.shape = self.indices.shape
        self.max = np.array(np.max(self.indices, axis=0), dtype=int)
        self.min = np.array(np.min(self.indices, axis=0), dtype=int)
        self.sobol_tuples = self._get_sobol_tuple_list()

    def _get_sobol_tuple_list(self) -> list:
        """Generate list of all possible Sobol index id tuples (subscripts).

        Returns
        -------
        :
            List of Sobol tuples.
        """
        sobol_tuples = []
        for r in range(1, self.shape[1] + 1):
            sobol_tuples += list(itertools.combinations(range(1, self.shape[1] + 1), r))
        return sobol_tuples

    def get_index_number(self, indices: np.ndarray) -> np.ndarray:
        """Get enumeration number of indices.

        Get the row indices of the given multiindices such that
        `self.indices[rows] = indices`.

        Parameters
        ----------
        indices : np.ndarray
            Indices to get the number of.

        Returns
        -------
        :
            Array containing the enumeration numbers of the indices.
        """
        return np.array(
            [np.where((self.indices == index).all(axis=1))[0] for index in indices],
            dtype=int,
        ).flatten()

    def get_sobol_tuple_number(self, sobol_tuples: list[tuple]) -> np.ndarray:
        """Get enumeration indices of Sobol tuples.

        Parameters
        ----------
        sobol_tuples : list of tuple
            List of Sobol tuples.

        Returns
        -------
        :
            Array containing the enumeration number of the Sobol tuples.
        """
        return np.array([self.sobol_tuples.index(s) for s in sobol_tuples], dtype=int)

    def index_to_sobol_tuple(self, indices: np.ndarray) -> list[tuple]:
        """Map array of indices to their respective Sobol tuples.

        Parameters
        ----------
        indices : np.ndarray
            Array of multiindices.

        Returns
        -------
        :
            List of Sobol tuples.
        """
        sobol_tuples = [tuple(np.flatnonzero(index) + 1) for index in indices]
        return sobol_tuples

    def sobol_tuple_to_indices(
        self, sobol_tuples: tuple | list[tuple]
    ) -> list[np.ndarray]:
        """Map Sobol tuples to their respective indices.

        Parameters
        ----------
        sobol_tuples : tuple or list of tuple
            List of Sobol tuples.

        Returns
        -------
        :
            List of index arrays for each given Sobol tuple.
        """
        if isinstance(sobol_tuples, tuple):
            sobol_tuples = [sobol_tuples]
        assert isinstance(sobol_tuples, list)
        ret = []
        lookup_dict = {sobol_tuple: [] for sobol_tuple in self.sobol_tuples}
        index_sobol_tuple_list = self.index_to_sobol_tuple(self.indices)
        for sobol_tuple, index in zip(index_sobol_tuple_list, self.indices):
            if len(sobol_tuple) > 0:
                lookup_dict[sobol_tuple] += [index]
        for sobol_tuple in sobol_tuples:
            ret += [np.array(lookup_dict[sobol_tuple], dtype=int)]
        return ret


def sort_index_array(indices: np.ndarray) -> np.ndarray:
    """Sort multiindices and remove duplicates.

    Sort rows of `indices` by sum of multiindex and remove duplicate
    multiindices.

    Parameters
    ----------
    indices : np.ndarray
        Index list before sorting.

    Returns
    -------
    :
        Sorted index array.
    """
    sorted_indices = np.unique(indices, axis=0)
    if sorted_indices.size == 0:
        return sorted_indices
    idx = np.argsort(np.sum(sorted_indices, axis=1))
    sorted_indices = sorted_indices[idx]
    return np.array(sorted_indices, dtype=int)


def union(index_list: list[np.ndarray]) -> np.ndarray:
    """Build union of multiindex sets.

    Given sparse index sets :math:`\\Lambda_1, \\dots, \\Lambda_N`,
    compute :math:`\\Lambda=\\Lambda_1\\cup\\dots\\cup\\Lambda_N`.

    Parameters
    ----------
    index_list : list of np.ndarray
        List of multiindex arrays.

    Returns
    -------
    :
        Array with all multiindices.
    """
    all_indices = np.concatenate(index_list, axis=0)
    return sort_index_array(all_indices)


def intersection(index_list: list[np.ndarray]) -> np.ndarray:
    """Intersect list of multiindex sets.

    Given sparse index sets :math:`\\Lambda_1, \\dots, \\Lambda_N`,
    compute :math:`\\Lambda=\\Lambda_1\\cap\\dots\\cap\\Lambda_N`.

    Parameters
    ----------
    index_list : list[np.ndarray]
        List of index sets.

    Returns
    -------
    :
        Intersection of index sets.
    """
    assert np.all(s.shape[1] == index_list[0].shape[1] for s in index_list)
    ret = index_list[0]
    for indices in index_list[1:]:
        ret = np.array(
            [x for x in set(tuple(x) for x in ret) & set(tuple(x) for x in indices)]
        )
    return sort_index_array(np.array(ret))


def set_difference(indices: np.ndarray, subtract: np.ndarray) -> np.ndarray:
    """Set difference of two index arrays.

    Given two sparse index sets :math:`\\Lambda_1` and :math:`\\Lambda_2`,
    compute :math:`\\Lambda=\\Lambda_1\\setminus\\Lambda_2`.

    Parameters
    ----------
    indices : np.ndarray
        Index array multiindices are taken out of.
    subtract : np.ndarray
        Indices that are taken out of the original set.

    Returns
    -------
    :
        Set difference of both index arrays.
    """
    indices = sort_index_array(indices)
    subtract = sort_index_array(subtract)
    assert indices.shape[1] == subtract.shape[1]
    idxs = []
    for mdx in subtract:
        idx = np.where((indices == mdx).all(axis=1))[0]
        assert idx.size < 2
        if idx.size == 1:
            idxs += [idx]
    return np.delete(indices, np.array(idxs, dtype=int).flatten(), axis=0)


def tensor_set(
    shape: list[int] | tuple[int] | np.ndarray,
    lower: list[int] | tuple[int] | np.ndarray | None = None,
) -> np.ndarray:
    """Create a tensor index set.

    For given upper and lower bounds
    :math:`0 \\leq \\ell_m < u_m \\in \\mathbb{N}_0` with
    :math:`m=1,\\dots,M\\in\\mathbb{N}`, the tensor index set (n-D cube) is
    given by

    .. math::
        \\Lambda = \\{ \\mu\\in\\mathbb{N}_0^M \\ \\vert\\ \\ell_m \\leq \\mu_m \\leq u_m \\mbox{ for } m=1,\\dots,M\\}.

    Parameters
    ----------
    shape : array_like
        Shape of the tensor, enumeration starting from 0.
    lower : array_like, default = None
        Starting values for each dimension of the tensor set. If None, all
        dimensions start with 0.

    Returns
    -------
    :
        Array with all possible multiindices in tensor set.

    See Also
    --------
    pythia.misc.cart_prod, pythia.index.lq_bound_set, pythia.index.simplex_set

    Examples
    --------
    Create the tensor product multiindices :math:`\\{0, 1\\}\\times\\{0, 1\\}`

    >>> pt.index.tensor_set([2, 2])
    array([[0, 0],
           [0, 1],
           [1, 0],
           [1, 1]])

    Create 3D univariate multiindices :math:`\\{0\\}\\times\\{1,\\dots, 4\\}\\times\\{0\\}`

    >>> pt.index.tensor_set([1, 5, 1], [0, 1, 0])
    array([[0, 1, 0],
           [0, 2, 0],
           [0, 3, 0],
           [0, 4, 0]])

    Create 1D indices similar to ``np.arange(1, 5, dtype=int).reshape(-1, 1)``

    >>> pt.index.tensor_set([5], [1])
    array([[1],
           [2],
           [3],
           [4]])
    """
    shape = np.array(shape, dtype=int)
    if lower is None:
        lower = np.zeros(shape.size, dtype=int)
    elif isinstance(lower, (list, tuple)):
        lower = np.array(lower, dtype=int)
    assert shape.size == lower.size
    univariate_dims = [np.arange(low, up, dtype=int) for low, up in zip(lower, shape)]
    if shape.size > 1:
        ret = pt.misc.cart_prod(univariate_dims)
    else:
        ret = np.array(univariate_dims).T
    return sort_index_array(ret)


def lq_bound_set(
    dimensions: list[int] | tuple[int] | np.ndarray, bound: float, q: float = 1
) -> np.ndarray:
    """Create set of multiindices with bounded :math:`\\ell^q`-norm.

    For given dimensions :math:`d \\in \\mathbb{N}^M`, bound
    :math:`b \\in \\mathbb{R}_{>0}` and norm factor
    :math:`q \\in \\mathbb{R}_{>0}`, the :math:`\\ell^q`-norm index set is
    given by

    .. math::
        \\Lambda = \\{ \\mu\\in [d_1]\\times\\dots\\times [d_M] \\ \\vert\\ \\Vert \\mu \\Vert_{\\ell^q} \\leq b\\},

    where :math:`[d_m]=\\{0, \\dots, d_m-1\\}` and

    .. math::
        \\Vert \\mu \\Vert_{\\ell^q} = \\Bigl(\\sum_{m=1}^M \\mu_m^q\\Bigr)^{\\frac{1}{q}}.

    Parameters
    ----------
    dimensions : list[int] | tuple[int] | np.ndarray
        Dimensions for each component, i.e., indices from ``0`` to
        ``dimension-1``.
    bound : float
        Bound for the :math:`\\ell^q`-norm.
    q : float, optional
        Norm factor.

    Returns
    -------
    :
        Array with all possible multiindices with bounded :math:`\\ell^q`-norm.

    See Also
    --------
    pythia.index.tensor_set, pythia.index.simplex_set

    Examples
    --------
    >>> pt.index.lq_bound_set([5, 5], 4, 0.5)
    array([[0, 0],
           [0, 1],
           [1, 0],
           [0, 2],
           [1, 1],
           [2, 0],
           [0, 3],
           [3, 0],
           [0, 4],
           [4, 0]])
    """
    assert np.all([d > 0 for d in dimensions]) and bound > 0 and q > 0
    all_indices = tensor_set(dimensions)
    rows = np.where(np.power(np.sum(all_indices**q, axis=1), 1 / q) <= bound)[0]
    return sort_index_array(all_indices[rows])


def simplex_set(dimension: int, maximum: int) -> np.ndarray:
    """Create a simplex index set.

    For given dimension :math:`M\\in\\mathbb{N}` and maximum
    :math:`d\\in\\mathbb{N}` the simplex index set is given by

    .. math::
        \\Lambda = \\{ \\mu\\in\\mathbb{N}_0^M \\ \\vert\\ \\sum_{m=1}^M \\mu_m \\leq d\\}.

    Notes
    -----
    Limiting the absolute value of the multiindices creates a simplex in
    :math:`\\mathbb{N}_0^M`, which motivates the name of the function.
    As an example, in two dimensions this gives us points inside a triangle
    limited by the axes and the line :math:`x_1 + x_2 = d`.

    Parameters
    ----------
    dimension : int
        Dimension of the multiindices.
    maximum : int
        Maximal sum value for the multiindices.

    Returns
    -------
    :
        Array with all possible multiindices in simplex set.

    See Also
    --------
    pythia.index.lq_bound_set, pythia.index.tensor_set

    Examples
    --------
    >>> pt.index.simplex(2, 2)
    array([[0, 0],
           [0, 1],
           [1, 0],
           [0, 2],
           [1, 1],
           [2, 0]])
    """
    assert dimension > 0 and maximum > 0
    return lq_bound_set([maximum + 1] * dimension, maximum, 1)
