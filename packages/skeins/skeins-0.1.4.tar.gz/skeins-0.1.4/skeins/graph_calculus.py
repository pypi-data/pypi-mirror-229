"""
Implements graph calculus, as described in: 
- https://akshay.bio/variable-expectations/graph-calculus/
"""


import numpy as np, scipy
from .graph_construction import symmetric_part, asymmetric_part


def grad_op_graph(fn, adj_mat):
    """Gradient of a function on a graph with n vertices.

    Parameters
    ----------
    fn : ndarray
        A function on vertices (n-dimensional vector)
    adj_mat : sparse matrix
        (n x n) adjacency matrix of graph
    
    Returns
    -------
    grad : ndarray
        (n x n) matrix of gradients on edges (directed graph)
    """
    return adj_mat.multiply(fn) - adj_mat.multiply(fn).T


def _compute_transitions_asym(adj_mat):
    W = symmetric_part(adj_mat)
    recip = np.reciprocal(np.asarray(W.sum(axis=0)).astype(np.float64))
    recip[np.isinf(recip)] = 0
    return scipy.sparse.spdiags(recip, 0, W.shape[0], W.shape[0]).dot(W)


def laplacian_op_graph(adj_mat, normalize=True):
    """Laplacian of a function over the n vertices of a graph.
    
    Parameters
    ----------
    adj_mat : sparse matrix
        (n x n) adjacency matrix of graph
    normalize: bool
        Whether to degree-normalize the Laplacian matrix. 
    
    Returns
    -------
    lapmat : sparse matrix
        Laplacian matrix (n x n) of the graph.
    """
    if not normalize:
        lapmat = scipy.sparse.diags(np.ravel(adj_mat.sum(axis=0))) - adj_mat
    else:
        lapmat = scipy.sparse.identity(adj_mat.shape[0]) - _compute_transitions_asym(adj_mat)
    return lapmat


def div_op_graph(field_mat, adj_mat):
    """Divergence of a function in a neighborhood on a graph with n vertices. 

    Parameters
    ----------
    field_mat : sparse matrix
        A vector field (function on edges, i.e. (n x n) matrix-valued)
    adj_mat : sparse matrix
        (n x n) adjacency matrix of graph
    
    Returns
    -------
    div : ndarray
        n-length array of vertex-wise divergence values.
    """
    trans_mat = _compute_transitions_asym(adj_mat)
    return np.ravel(trans_mat.multiply(graph_construction.asymmetric_part(field_mat)).sum(axis=1))


def curl_op_graph(field_mat, adj_mat):
    """Curl of a function on edges of a graph with n vertices.
    
    Parameters
    ---------- 
    field_mat : sparse matrix
        A vector field (function on edges, i.e. (n x n) matrix-valued)
    adj_mat : sparse matrix
        (n x n) adjacency matrix of graph
    
    Returns
    -------
    div : sparse matrix
        Matrix of curl associated with each edge.
    """
    np.reciprocal(adj_mat.data, out=adj_mat.data)
    return adj_mat.multiply(symmetric_part(field_mat))


def helmholtz(
    field_mat, 
    adj_mat, 
    given_divergence=None
):
    """Compute Helmholtz decomposition of a function over the edges of a given graph with n vertices. 

    If this function is F, the decomposition is given by:
        F = - ∇P + S + U
    where P is a scalar potential, S is a symmetric potential, and U is a "harmonic" potential which is divergence-free, and 0 when field_mat is symmetric.

    Parameters
    ----------
        field_mat : sparse matrix
            A vector field (function on edges, i.e. (n x n) matrix-valued)
        adj_mat: sparse matrix
            (n x n) adjacency matrix of graph.
        given_divergence: a given divergence function over vertices. 
            Replaces the use of field_mat if the source/sink info is known.
    
    Returns
    -------
        vertex_potential : array
            Length-n array of vertex potentials.
        edge_potential : sparse matrix
            (n x n) matrix of edge potentials.
    """
    laplacian_op = laplacian_op_graph(adj_mat)
    if given_divergence is not None:
        sympart = scipy.sparse.csr_matrix(adj_mat.shape)
        potential = scipy.sparse.linalg.lsmr(
            laplacian_op, 
            given_divergence
        )
    else:
        sympart = symmetric_part(field_mat)
        potential = scipy.sparse.linalg.lsmr(
            laplacian_op, 
            div_op_graph(field_mat, adj_mat)
        )
    return (potential[0], sympart)



