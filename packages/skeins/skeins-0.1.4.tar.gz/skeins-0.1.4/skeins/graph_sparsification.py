"""
Implements label propagation and related methods, as described in: 
- https://akshay.bio/blog/graph-prediction-diffusion/
"""


import numpy as np, scipy


def spectral_sparsify(
    adj_mat, q=None, epsilon=1e-1, eta=1e-3, max_iters=1000, convergence_after=100,
    tolerance=1e-2, log_every=10, prevent_vertex_blow_up=False
):
    """ Computes a spectral sparsifier of the graph given by an adjacency matrix. 

    Uses the sampling procedure given in [1]_.
    
    Parameters:
    ----------
    adj_mat : sp.csr_matrix, shape [N, N]
        The adjacency matrix of the graph.
    q : int or None
        The number of samples for the sparsifier. If None q will be set to N * log(N) / (epsilon * 2)
    epsilon : float
        The desired spectral similarity of the sparsifier.
    eta : float
        Step size for the gradient descent when computing resistances.
    max_iters : int
        Maximum number of iterations when computing resistances.
    convergence_after : int
        If the loss did not decrease significantly for this amount of iterations, the gradient descent will abort.
    tolerance : float
        The minimum amount of energy decrease that is expected for iterations. If for a certain number of iterations
        no overall energy decrease is detected, the gradient descent will abort.
    prevent_vertex_blow_up : bool
        If the probabilities will be tweaked in order to ensure that the vertices are not blown up too much. 
        Note that this will only guarantee a spectral closeness up to a factor of 2 * epsilon.
    log_every : int
        How often to log the current loss (once every `log_every` iterations).
    
    Returns:
    --------
    H : sp.csr_matrix, shape [N, N]
        Sparsified graph with at most q edges.

    References
    ----------
    .. [1] Daniel A. Spielman and Nikhil Srivastava, Graph sparsification by 
           effective resistances, Proceedings of the fortieth annual ACM 
           symposium on Theory of computing, pp. 563-568. 2008.
    """
    if q is None:
        q = int(np.ceil(adj_mat.shape[0] * np.log(adj_mat.shape[0]) / (epsilon ** 2)))   # or 6n*ln(n) , by https://www.cs.ubc.ca/~nickhar/Cargese3.pdf
    edges = adj_mat.nonzero()
    Z = calculate_reduced_resistances(adj_mat, epsilon=epsilon, max_iters=max_iters, convergence_after=convergence_after, eta=eta, tolerance=tolerance, compute_exact_loss=False)
    R = compute_effective_resistances(Z, edges)
    return sample_sparsifier(adj_mat, q, R, edges, prevent_vertex_blow_up=prevent_vertex_blow_up)


def calculate_reduced_resistances(
    adj_mat, 
    epsilon=1e-1, eta=1e-3, max_iters=1000, convergence_after = 10,
    tolerance=1e-2, log_every=10, compute_exact_loss=False
):
    """ Computes the Z matrix using gradient descent.
    
    Parameters:
    -----------
    adj_mat : sp.csr_matrix
        The adjacency matrix of the graph.
    epsilon : float
        Tolerance for deviations w.r.t. spectral norm of the sparsifier. Smaller epsilon lead to a higher
        dimensionality of the Z matrix.
    eta : float
        Step size for the gradient descent.
    max_iters : int
        Maximum number of iterations.
    convergence_after : int
        If the loss did not decrease significantly for this amount of iterations, the gradient descent will abort.
    tolerance : float
        The minimum amount of energy decrease that is expected for iterations. If for a certain number of iterations
        no overall energy decrease is detected, the gradient descent will abort.
    log_every : int
        Log the loss after each `log_every` iterations.
    compute_exact_loss : bool
        Only for debugging. If set it computes the actual pseudo inverse without down-projection and checks if
        the pairwise distances in Z's columns are the same with respect to the forbenius norm.
        
    Returns:
    --------
    Z : ndarray, shape [k, N]
        Matrix from which to efficiently compute approximate resistances.
    """
    # Compute L, S, B
    L = sp.csr_matrix(sp.csgraph.laplacian(adj_mat))
    rows, cols = adj_mat.nonzero()
    weights = np.sqrt(np.array(adj_mat[rows, cols].tolist()))
    S = sp.diags(weights, [0])
    # Construct signed edge incidence matrix
    num_vertices = adj_mat.shape[0]
    num_edges = S.shape[0]
    assert(num_edges == len(rows) and num_edges == len(cols))
    B = sp.coo_matrix((
        ([1] * num_edges) + ([-1] * num_edges),
        (list(range(num_edges)) * 2, list(rows) + list(cols))
    ), shape=[num_edges, num_vertices])

    k = int(np.ceil(np.log(B.shape[1] / epsilon**2)))
    Y_red = compute_reduced_vertices()
    
    # Use gradient descent to solve for Z
    Z = np.random.randn(k, L.shape[1])
    best_loss = np.inf
    best_iter = np.inf
    for it in range(max_iters):
        eta_t = eta  # Constant learning rate
        eta_t = eta * (1.0/np.sqrt(it + 10))
        residual = Y_red - sp.csr_matrix.dot(Z, L)
        loss = np.linalg.norm(residual)
        if it % log_every == 0: 
            print(f'Loss before iteration {it}: {loss}')
            if compute_exact_loss:
                pairwise_dist = Z.T.dot(Z)
                exact_loss = np.linalg.norm(pairwise_dist - pairwise_dist_gnd)
                print(f'Loss w.r.t. exact pairwise distances {exact_loss}')
        if loss + tolerance < best_loss:
            best_loss = loss
            best_iter = it
        elif it > best_iter + convergence_after:
            # No improvement for 10 iterations
            print(f'Convergence after {it - 1} iterations.')
            break
        Z += eta_t * L.dot(residual.T).T
    return Z


def compute_effective_resistances(Z, edges):
    """
    Parameters
    ----------
    Z : sparse matrix
        A (k x n) matrix from which to efficiently compute approximate effective resistances.
    edges : tuple
        A tuple of two lists: the row and column indices of the respective edges.
    
    Returns
    -------
    R : sparse matrix
        Effective resistances for each edge.
    """
    rows, cols = edges
    R = []
    for i, j in zip(rows, cols):
        R.append(np.linalg.norm(Z[:, i] - Z[:, j]) ** 2)
    return np.array(R)


def sample_sparsifier(adj_mat, num_edges, R, ultrasparsifier=False):
    """
    Parameters
    ----------
    adj_mat : sparse matrix
        The adjacency matrix of the graph.
    num_edges : int
        The number of samples for the sparsifier.
        
    Returns
    -------
    H : sparse matrix
        The adjacency matrix of the sparsified graph with at most num_edges edges.
    """
    rows, cols, R = compute_exact_resistances(adj_mat)
    weights = np.array(adj_mat[rows, cols].tolist())   # Effective resistances (approximate) for each edge.
    probs = compute_sampling_probs(adj_mat, R, ultrasparsifier=ultrasparsifier)
    sampled = np.random.choice(len(probs), num_edges, p=probs, replace=True)
    H = sp.lil_matrix(adj_mat.shape)
    for idx in sampled:
        H[rows[idx], cols[idx]] += weights[idx] / num_edges / probs[idx]
    return H.tocsr()


def compute_exact_resistances(adj_mat):
    """Compute effective resistance between all pairs of vertices in the graph.

    Parameters
    ----------
    adj_mat : sparse matrix
        The adjacency matrix of the graph.

    Returns
    -------
    rows : ndarray
        Row indices of the edges.
    cols : ndarray
        Column indices of the edges.
    R : ndarray
        Effective resistances for each edge.
    """
    if scipy.sparse.issparse(adj_mat):
        L = sp.csgraph.laplacian(adj_mat).tocsr()
        L_inv = np.linalg.pinv(L.todense())
    else:
        L = sp.csgraph.laplacian(adj_mat)
        L_inv = np.linalg.pinv(L)
    rows, cols = adj_mat.nonzero()
    R = []
    for i, j in zip(rows, cols):
        R.append(L_inv[i, i] + L_inv[j, j] - L_inv[j, i] - L_inv[i, j])
    return (rows, cols, R)


def compute_sampling_probs(adj_mat, R, ultrasparsifier=False):
    """Compute sampling probabilities for each edge, from the effective resistances.

    Parameters
    ----------
    adj_mat : sparse matrix
        The adjacency matrix of the graph.
    R : sparse matrix
        Matrix of effective resistances
    ultrasparsifier : bool
        Whether to use ultrasparsifier (change probabilities so that no edge gets scaled up much). 
        Only guarantees spectral closeness up to 2 * epsilon, but with the benefit of lowering variance.
    """
    rows, cols = adj_mat.nonzero()
    weights = np.array(adj_mat[rows, cols].tolist())
    probs = weights * R
    probs /= np.sum(probs)
    if ultrasparsifier:
        degrees = adj_mat.sum(1)[np.array((rows, cols))].squeeze().T
        mins = 1 / np.min(degrees, axis=1) / adj_mat.shape[0]
        probs += mins
        probs /= 2
    # probs = probs.reshape((probs.shape[0], 1))
    probs /= np.sum(probs)
    return np.ravel(probs)
