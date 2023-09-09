"""
File: pythia/chaos.py
Author: Nando Hegemann
Gitlab: https://gitlab.com/Nando-Hegemann
Description: Sample-based computation of polynomial chaos expansion.
SPDX-License-Identifier: LGPL-3.0-or-later OR Hippocratic-3.0-ECO-MEDIA-MIL
"""
import warnings
import math
import psutil
import numpy as np
import pythia as pt


class PolynomialChaos:
    """Computation of sparse polynomial chaos expansion.

    Parameters
    ----------
    params : list of `pt.parameter.Parameter`
        List of stochastic parameters.
    index_set : pt.index.IndexSet
        Index set for sparse polynomial chaos expansion.
    x_train : array_like
        Parameter realizations for training.
    weights : array_like
        Regression weights for training.
    fEval : array_like
        Function evaluation for training.
    coefficients : array_like, default=None
        Polynomial expansion coefficients. If given, the coefficients are not
        computed during initiation. This can be used to load a chaos expansion.
    """

    def __init__(
        self,
        params: list[pt.parameter.Parameter],
        index_set: pt.index.IndexSet,
        x_train: np.ndarray,
        w_train: np.ndarray,
        y_train: np.ndarray,
        coefficients: np.ndarray | None = None,
    ) -> None:
        """Initiate the computation of the PC expansion of a function."""
        assert x_train.ndim == 2 and x_train.shape[1] == len(params)
        assert w_train.ndim == 1 and w_train.size == x_train.shape[0]
        assert y_train.ndim == 2 and y_train.shape[0] == x_train.shape[0]

        self.parameters = params
        self.index_set = index_set
        self.x_train = x_train
        self.w_train = w_train
        self.y_train = y_train

        self.n_samples, self.sdim = x_train.shape
        self.ydim = y_train.shape[1]

        self.univariate_pdfs = [
            pt.sampler.assign_sampler(param) for param in self.parameters
        ]
        self.pdf = pt.sampler.ParameterSampler(self.parameters).pdf
        self.univariate_bases = pt.basis.univariate_basis(
            self.parameters, self.index_set.max
        )
        self.basis = pt.basis.multivariate_basis(
            self.univariate_bases, self.index_set.indices
        )

        self.gramian, self.basis_eval_mat = self._assemble_matrices()
        if coefficients is None:
            self.coefficients = self._fit()
        else:
            assert coefficients.shape == (index_set.shape[0], self.ydim)
            self.coefficients = coefficients
        self.sobol = self._compute_sobol_indices()

    @property
    def mean(self) -> np.ndarray:
        """Mean of the PC expansion."""
        idx = self.index_set.get_index_number(np.zeros((1, self.sdim), dtype=int))
        return self.coefficients[idx].flatten()

    @property
    def var(self) -> np.ndarray:
        """Variance of the PC expansion."""
        if self.index_set.shape[0] == 1 and np.all(self.index_set.indices == 0):
            return np.zeros(self.ydim)
        return np.sum(self.coefficients**2, axis=0).flatten() - self.mean**2

    @property
    def std(self) -> np.ndarray:
        """Standard deviation of the PC expansion."""
        return np.sqrt(self.var)

    def _assemble_matrices(self) -> tuple[np.ndarray, np.ndarray]:
        """Assemble Gramian and basis evaluation matrix.

        Assemble the information matrix :math:`A` and the basis evaluation
        matrix :math:`\\Psi` with the regression points of the PC expansion.
        The basis evaluation matrix :math:`\\Psi` is given by

        .. math::
            \\Psi_{kj} = \\operatorname{basis}[j](\\operatorname{regPoints}[k]).

        Returns
        -------
        gramian : np.ndarray
            Empirical Gramian matrix.
        psi_mat : np.ndarray
            Basis evaluation matrix :math:`\\Psi`.
        """
        batch_size = get_gram_batchsize(len(self.basis))
        psi_mat = np.array([p(self.x_train) for p in self.basis])
        gramian = np.zeros((len(self.basis), len(self.basis)))
        for batch in pt.misc.batch(range(self.x_train.shape[0]), batch_size):
            mat_1 = psi_mat[:, batch].reshape(1, len(self.basis), len(batch))
            mat_2 = psi_mat[:, batch].reshape(len(self.basis), 1, len(batch))
            gramian += np.sum(self.w_train[batch] * mat_1 * mat_2, axis=-1)
        return gramian, psi_mat.T

    def _fit(self) -> np.ndarray:
        """Compute polynomial chaos expansion coefficients.

        Compute the PC coefficients with linear regression. The coefficients
        are given by

        .. math::
            S = A^(-1) * \\Psi^T * W * F_\\mathrm{ex}

        where the Gram matrix :math:`A` is of full rank but may be ill
        conditioned.  :math:`F_\\mathrm{ex}` is an array containing the values
        of f evaluated at the required regression points. For more detail on
        the Gram matrix or :math:`\\Psi`, see `assemble_matrices()`.

        Returns
        -------
        :
            Polynomial chaos expansion coefficients.
        """
        u, s, vh = np.linalg.svd(self.gramian)
        gramian_inv = np.dot(vh.T, np.dot(np.diag(1 / s), u.T))
        W = self.w_train.reshape(-1, 1)
        coefficients = np.linalg.multi_dot(
            [gramian_inv, self.basis_eval_mat.T, W * self.y_train]
        )
        return coefficients

    def _compute_sobol_indices(self) -> np.ndarray:
        """Compute Sobol indices.

        The Sobol coefficients are given as

        .. math::
            S_{i_1,...,i_k} = \\sum_{\\alpha\\in\\mathcal{M}} f_\\alpha(x)^2

        where :math:`\\mathcal{M} = { \\alpha | \\alpha_{i_j} != 0 for j = 1,...,k }`.
        """
        sobol = np.zeros([len(self.index_set.sobol_tuples), self.ydim])
        # mask components of f with zero variance
        nz_idx = np.nonzero(self.var)
        for idx, sdx in enumerate(self.index_set.sobol_tuples):
            _mdx = self.index_set.sobol_tuple_to_indices([sdx])[0]
            rows = self.index_set.get_index_number(_mdx)
            coeffs = self.coefficients[rows]
            sobol[idx, nz_idx] = (
                np.sum(coeffs[:, nz_idx] ** 2, axis=0) / self.var[nz_idx]
            )
        return sobol

    def eval(
        self, x: np.ndarray, partial: list[int] | dict | None = None
    ) -> np.ndarray:
        """Evaluate the (partial derivative of the) PC approximation.

        Parameters
        ----------
        x : np.ndarray
            Parameter realizations in which the approximation is evaluated.
        partial : list[int] | dict | None, optional
            Number of derivatives for each parameter component.
            If a list is given, length has to be the number of parameters.
            Ordering of list is according to ``self.parameters``.
            If a dict is given, keys have to be subset of parameter names.

        Returns
        -------
        :
            Evaluation of polynomial expansion in x values.

        Examples
        --------
        Given two parameters :math:`x_1` and :math:`x_2`

        >>> param1 = pt.parameter.Parameter("x1", [-1, 1], "uniform")
        >>> param2 = pt.parameter.Parameter("x2", [-1, 1], "uniform")

        a corresponding polynomial chaos approximation for a function :math:`f\\colon (x_1,x_1) \\mapsto y`

        >>> surrogate = pt.chaos.PolynomialChaos([param1, param2], ...)

        and an array the surrogate should be evaluated in

        >>> x_test = np.random.uniform(-1, 1, (1000, 2))

        we can evaluate the surrogate with

        >>> y_approx = surrogate.eval(x_test)

        To obtain partial a partial derivative of the approximation, e.g., :math:`\\frac{\\partial^2f}{\\partial x_2^2}`, specify a list

        >>> y_approx = surrogate.eval(x_test, partial=[0, 2])

        or a dictionary with parameter names and number of partial derivates

        >>> y_approx = surrogate.eval(x_test, partial={'x2':2})
        """
        if x.ndim < 1 or x.ndim > 2:
            raise ValueError(f"Wrong ndim: '{x.ndim}'")
        if x.ndim == 1:
            x.shape = 1, -1  # TODO: need to do this: x = x.reshape(1, -1)?
        c = self.coefficients.reshape(self.coefficients.shape[0], 1, -1)
        if partial is None:
            basis = self.basis
        else:
            if isinstance(partial, dict):
                _param_names = [p.name for p in self.parameters]
                # check that all keys in partial are parameter names
                assert set(partial.keys()).issubset(set(_param_names))
                _partial = [0] * len(_param_names)
                for k, v in partial.items():
                    _partial[_param_names.index(k)] = v
            else:  # partial already is a list of int
                _partial = partial
            basis = pt.basis.multivariate_basis(
                self.univariate_bases, self.index_set.indices, _partial
            )
        eval_mat = np.array([b(x) for b in basis])
        eval_mat.shape = eval_mat.shape[0], eval_mat.shape[1], 1
        return np.sum(c * eval_mat, axis=0)


def find_optimal_indices(
    params: list[pt.parameter.Parameter],
    x_train: np.ndarray,
    w_train: np.ndarray,
    y_train: np.ndarray,
    max_terms: int = 0,
    threshold: float = 1e-03,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute optimal multiindices of polynomial chaos expansion.

    Heuristical approach to compute almost optimal multiindices for a
    polynomial chaos expansion based on an estimate of the Sobol
    index values.

    Parameters
    ----------
    params : list of pythia.Parameters.Parameter
        Random parameters of the problem.
    x_train : array_like
        Sample points for training
    w_train : array_like
        Weights for training.
    y_train : array_like
        Function evaluations for training.
    max_terms : int, default=0
        Maximum number of expansion terms. Number of expansion terms is chosen
        automatically for `max_terms=0`.
    threshold : float, default=1e-03
        Truncation threshold for Sobol indices. Smallest Sobol values with sum
        less then ``threshold`` are ignored.

    Returns
    -------
    indices :
        Array with multiindices.
    sobol :
        Crude intermediate approximation of Sobol indices.

    Notes
    -----
    To find reasonable candidates for the sparse polynomial chaos expansion,
    first an expansion with a large simplex index set is computed.
    The simplex index set uses the same maximum dimension in each component
    and is designed to have at least ``max_terms`` many elements.
    With this index set a polynomial chaos expansion is computed.
    The computed Sobol indices are then ordered and the largest contributions
    are collected by a Dörfler marking strategy.
    Then a new index set is assembled by including a downward closed subset of
    polynomial chaos coefficient indices for each selected Sobol index tuple.
    The number of chosen indices for each selected Sobol index tuple is weighted
    by the respective Sobol index value.
    """
    assert 0 <= threshold < 1
    # set maximal number of expansion terms
    n_samples, dim = x_train.shape
    if max_terms > 0:
        _max_terms = max_terms
    else:
        _max_terms = int(n_samples / np.log(n_samples) / 2)
    if _max_terms > int(n_samples / np.log(n_samples) / 2):
        warnings.warn("Gramian may become ill conditioned.")

    # compute crude approximation of Sobol coefficients
    deg = 1
    for _deg in range(2, 1000):
        n_terms = (
            math.factorial(_deg + dim) / math.factorial(_deg) / math.factorial(dim)
        )
        if n_terms > _max_terms:
            break
        deg = _deg
    _indices = pt.index.simplex_set(dim, deg)
    index_set = pt.index.IndexSet(_indices)
    surrogate = PolynomialChaos(params, index_set, x_train, w_train, y_train)

    # sort Sobol coefficients by largest and mark top threshold percent.
    idx, _, marker = pt.misc.doerfler_marking(
        np.sum(surrogate.sobol, axis=1), threshold=1 - threshold
    )

    # assemble adaptive choice of multiindices
    indices = assemble_indices(idx[:marker], index_set.sobol_tuples, _max_terms)

    return indices, surrogate.sobol


def assemble_indices(
    enum_idx: list[int] | tuple[int] | np.ndarray,
    sobol_tuples: list[tuple],
    max_terms: int,
) -> np.ndarray:
    """Compute automatic choice of multiindices.

    Parameters
    ----------
    enum_idx : np.ndarray
        Sorted enumeration indices according to magnitude of Sobol indices.
    sobol_tuples : list of tuple
        List of Sobol subscript tuples.
    max_terms : int
        Maximum number of expansion terms.

    Returns
    -------
    indices : np.ndarray
        Array of (sparse) optimal multiindices.
    """
    dim = max(len(sdx) for sdx in sobol_tuples)
    n_terms_per_idx = int((max_terms - 1) / len(enum_idx))
    indices_list = []
    for idx in enum_idx:
        components = [s - 1 for s in sobol_tuples[idx]]  # current sdx
        deg = int(n_terms_per_idx ** (1 / len(components)) + 1)
        tmp_indices = pt.index.tensor_set(
            [deg + 2 if j in components else 1 for j in range(dim)],
            [1 if j in components else 0 for j in range(dim)],
        )
        indices_list += [tmp_indices[:n_terms_per_idx]]
    indices = pt.index.sort_index_array(
        np.concatenate([np.zeros((1, dim))] + indices_list, axis=0)
    )
    return indices


def get_gram_batchsize(dim: int, save_memory: float = 1025**3 / 2) -> int:
    """Compute memory allocation batch sizes for information matrix.

    Compute the maximal number of samples in each batch when assembling the
    information matrix to be maximally memory efficient and avoid OutOfMemory
    errors.

    Parameters
    ----------
    dim : int
        Number of rows/columns of information matrix.
    save_memory : int, default=3*1025/2
        Memory (in bytes), that should be kept free. The default is equivalent
        to 512 MB.

    Returns
    -------
    :
        Batchsize for assembling of information matrix.
    """
    available_memory = psutil.virtual_memory().available
    mem = available_memory - save_memory
    n = int(mem / 8 / dim**2)
    if n < 1:
        # There is less memory available than required for at least one sample.
        raise MemoryError("Not enough free memory.")
    else:
        return n


if __name__ == "__main__":
    pass
