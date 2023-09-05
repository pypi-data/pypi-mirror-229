"""
Implements graph embedding methods, as described in: 
- https://akshay.bio/blog/embedding-methods/
"""


import numpy as np, scipy, sklearn
from .graph_construction import compute_diffusion_kernel


def compute_eigen(adj_mat, n_comps=2, sym=True):
    """Wrapper to compute eigendecomposition of a sparse matrix, e.g. for dimension reduction.

    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph.
    n_comps : int, optional
        Number of eigenvectors to return. Default: 2.
    sym : bool, optional
        Whether to symmetrize the transition matrix. Default: True.
    
    Returns
    -------
    eigvals : ndarray
        Vector with `n_comps` leading eigenvalues of the matrix.
    evecs : ndarray
        Matrix (n x `n_comps`), with the corresponding `n_comps` leading eigenvectors of the matrix.

    Notes
    -----
    `scipy.sparse.linalg.eigsh` is used here; we use `np.linalg.eigh` if we want 
    to support non-sparse matrices.
    """
    if sym:
        eigvals, evecs = scipy.sparse.linalg.eigsh(adj_mat.astype(np.float64), k=n_comps)
    else:
        # eigvals, evecs = scipy.sparse.linalg.eigs(adj_mat.astype(np.float64), k=n_comps)   # DON'T USE without further thresholding: complex-number underflow issues
        evecs, eigvals, _ = scipy.sparse.linalg.svds(adj_mat.astype(np.float64), k=n_comps)
    # eigvals, evecs = eigvals.astype(np.float32), evecs.astype(np.float32)
    sorted_ndces = np.argsort(np.abs(eigvals))[::-1]
    return eigvals[sorted_ndces], evecs[:, sorted_ndces]


def diffmap_proj(
    adj_mat, 
    t=None, 
    min_energy_frac=0.95, 
    n_dims=None, 
    n_comps=None, 
    return_eigvals=False, 
    embed_type='diffmap', 
    sym_compute=True, 
    sym_return=False
):
    """Compute diffusion map embedding.

    This [1]_ computes the diffusion map embedding for a graph, given its adjacency matrix.

    Assumes that {sym_return => sym_compute} holds, i.e. doesn't allow sym_compute==False and sym_return==True.
    Returns (n_comps-1) components, excluding the first which is the same for all data.

    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph.
    t : float, optional
        How much to run diffusion. Defaults to auto-computing this value for faithful dimension reduction.
    min_energy_frac : float, optional
        Minimum fraction of energy to retain in the first `n_dims` dimensions. 
        Defaults to 0.95.
    n_dims : int, optional
        Number of dimensions to return. Defaults to `n_comps`-1 if not given.
    n_comps : int, optional
        Number of components to use in computation of smoothed diffusion time. 
        Defaults to all components (i.e. n_dims-1), up to a maximum of 2000.
    return_eigvals : bool, optional
        Whether to return the eigenvalues as well. Defaults to False.
    embed_type : str, optional
        Type of embedding to compute, in ['naive', 'diffmap', 'commute']. Defaults to 'diffmap'.
    sym_compute : bool, optional
        Whether to compute the SVD on a symmetric matrix. Defaults to True.
    sym_return : bool, optional
        Whether to return the SVD of the symmetrized transition matrix. Defaults to False.
    
    Returns
    -------
    all_comps : ndarray
        Matrix (n x `n_dims`) with `n_dims` leading eigenvectors of the matrix.

    References
    ----------
    .. [1] Ronald R. Coifman, Stéphane Lafon, Diffusion maps, 
           Applied and computational harmonic analysis 21.1 (2006): 5-30.
    """
    if n_comps is None:     # When data are high-d dimensional with log2(d) \leq 14-16, 2K eigenvector computation is tolerably fast; change otherwise
        n_comps = min(2000, adj_mat.shape[0]-1)
    if n_dims is None:
        n_dims = n_comps - 1
    eigvals, evecs = compute_eigen(compute_diffusion_kernel(adj_mat, sym=sym_compute), n_comps=n_comps, sym=sym_compute)
    if sym_compute:
        evecs_sym = evecs
        evecs_unsym = np.multiply(evecs, np.outer(1.0/evecs[:,0].astype(np.float64), np.ones(evecs.shape[1])))
    else:
        evecs_unsym = evecs
    if sym_return:
        if not sym_compute:
            print("TODO: ERROR LOGGED HERE")
            return
        eigvecs_normalized = sklearn.preprocessing.normalize(np.real(evecs_sym), axis=0, norm='l2')
    else:
        eigvecs_normalized = sklearn.preprocessing.normalize(np.real(evecs_unsym), axis=0, norm='l2')
    
    if embed_type=='naive':
        all_comps = eigvecs_normalized
    if t is None:     # Use min_energy_frac to determine the fraction of noise variance 
        t = min_t_for_energy(eigvals, n_dims+1, min_energy_frac)
    if embed_type=='diffmap':
        frac_energy_explained = np.cumsum(np.power(np.abs(eigvals), t)/np.sum(np.power(np.abs(eigvals), t)))[n_dims]
        print("{} dimensions contain about {} fraction of the variance in the first {} dimensions (Diffusion time = {})".format(
            n_dims+1, frac_energy_explained, n_comps, t))
        all_comps = np.power(np.abs(eigvals), t) * eigvecs_normalized
    if embed_type=='commute':
        all_comps = np.power((1-np.abs(eigvals)), -t/2) * eigvecs_normalized
    if not return_eigvals:
        return all_comps[:,1:(n_dims+1)]     # Return n_dims dimensions, skipping the first trivial one.
    else:
        return (all_comps[:,1:(n_dims+1)], eigvals)    # Return the eigenvalues as well.


def heat_eigval_dist(eigvals, t):
    return np.power(np.abs(eigvals), t)/np.sum(np.power(np.abs(eigvals), t))


def min_t_for_energy(eigvals, desired_dim, min_energy_frac, max_t=None):
    """Calculate upper bound for t to capture desired fraction of variance. 

    The diffusion map at the returned value t* is such that 
    the first `desired_dim` dimensions of the diffusion map 
    capture at least `min_energy_frac` fraction of the variance.

    Parameters
    ----------
    eigvals : ndarray
        Eigenvalues of the matrix.
    desired_dim : int
        Number of embedding dimensions to capture variance within.
    min_energy_frac : float
        Minimum fraction of energy to retain in the `desired_dim` dimensions.
    max_t : float, optional
        Maximum value of t to search over. 
        Defaults to None, in which case it is set to log(100)/log(g) where g is the principal eigengap. 
        (If g=lbda1/lbda2, then g^t < 100 implies t < log(100)/log(g) , which is the worst case for variance reduction).
    
    Returns
    -------
    t : float
        Upper bound on t.
    """
    if max_t is None:
        max_t = np.log(100)/np.log(max(eigvals[0]/eigvals[1], 1.01)) # Don't change unless you know what you're doing!
    f = lambda t: (np.sum(heat_eigval_dist(eigvals, t)[:desired_dim]) - min_energy_frac)
    if f(0)*f(max_t) >= 0:    # since f is always nondecreasing this means the zero isn't in the interval
        return max_t if f(0) < 0 else 0
    return scipy.optimize.brentq(f, 0, max_t)

