"""
Implements graph construction methods. 
"""


import numpy as np, scipy


def symmetric_part(A):
    """Returns a symmetrized version of the input matrix.
    
    Parameters
    ----------
    A : ndarray or sparse matrix
        A square matrix.

    Returns
    -------
    A_sym : ndarray
        Symmetric part of A.
    """
    return 0.5*(A + A.T)


def asymmetric_part(A):
    """Returns an anti-symmetrized version of the input matrix.
    
    Parameters
    ----------
    A : ndarray or sparse matrix
        A square matrix.

    Returns
    -------
    A_sym : ndarray
        Anti-symmetric part of A.
    """
    return 0.5*(A - A.T)


def compute_diffusion_kernel(
    adj_mat, alpha=0.0, 
    normalize=True, sym=True, self_loops=False
):
    """Compute the diffusion kernel of a graph [1]_ , given its adjacency matrix.

    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph.
    alpha : float , The exponent of the diffusion kernel. 
        * 1 = Laplace-Beltrami (density)-normalized. 
        * 0.5 = normalized graph Laplacian (Fokker-Planck dynamics) [2]_.
        * 0 = classical graph Laplacian [default]. 
    normalize : bool
        Whether to normalize the transition matrix.
    sym : bool
        Whether the transition matrix normalization should be symmetric. (Relies on normalize==True).
        If True, the kernel is symmetric $D^{-1/2} A D^{1/2}$. If False, it is asymmetric $D^{-1} A$. 
    self_loops : bool
        Whether to add self-loops to the graph [3]_.

    Returns
    -------
    W : sparse matrix
        The diffusion's transition kernel calculated according to these parameters.
    
    References
    ----------
    .. [1] Ronald R. Coifman, Stéphane Lafon, Diffusion maps, 
           Applied and computational harmonic analysis 21.1 (2006): 5-30.
    .. [2] Boaz Nadler, Stephane Lafon, Ioannis Kevrekidis, Ronald Coifman, 
           Diffusion maps, spectral clustering and reaction coordinates of dynamical systems, 
           Applied and Computational Harmonic Analysis 21.1 (2006): 113-127.
    .. [3] Felix Wu, Amauri Souza, Tianyi Zhang, Christopher Fifty, Tao Yu, Kilian Weinberger, 
           Simplifying graph convolutional networks, International conference on machine learning, pp. 6861-6871. PMLR, 2019.
    """
    similarity_mat = symmetric_part(adj_mat)
    W = similarity_mat
    if alpha != 0:
        dens = np.asarray(similarity_mat.sum(axis=0))  # dens[i] is an estimate for the sampling density at point i.
        K = scipy.sparse.spdiags(np.power(dens, -alpha), 0, similarity_mat.shape[0], similarity_mat.shape[0])
        W = scipy.sparse.csr_matrix(K.dot(similarity_mat).dot(K))
    if self_loops:
        W = W + scipy.sparse.identity(W.shape[0])
    
    if not normalize:
        return W
    else:
        z = np.sqrt(np.asarray(W.sum(axis=0)).astype(np.float64))    # sqrt(density)
        recipsqrt = np.reciprocal(z)
        recipsqrt[np.isinf(recipsqrt)] = 0
        Zmat = scipy.sparse.spdiags(recipsqrt, 0, W.shape[0], W.shape[0])
        return Zmat.dot(W).dot(Zmat) if sym else Zmat.power(2).dot(W)


def triangle_kernel(gmat, ID='M1'):
    """Compute an adjacency matrix of triangle counts for a graph, given its adjacency matrix [1]_ .

    Parameters
    ----------
    gmat: sparse matrix
        A sparse adjacency matrix of the graph.
    ID: str , optional
        The type of triangle kernel to compute. Options in ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'].

    Returns
    -------
    c: sparse matrix
        The triangle kernel matrix. 
        Its (i,j)th entry is the number of triangles that i and j are both involved in.
    
    References
    ----------
    .. [1] A. R. Benson, D. F. Gleich, J. Leskovec, Higher-order organization 
           of complex networks, Science, 353(6295), 163-166, 2016.
    """
    Bmat = gmat.multiply(gmat.T)
    Umat = gmat - Bmat
    if ID == 'M1':
        c = np.dot(Umat, Umat).multiply(Umat.T)
        return c + c.T
    elif ID == 'M2':
        c = np.dot(Bmat, Umat).multiply(Umat.T) + np.dot(Umat, Bmat).multiply(Umat.T) + np.dot(Umat, Umat).multiply(Bmat)
        return c + c.T
    elif ID == 'M3':
        c = np.dot(Bmat, Bmat).multiply(Umat) + np.dot(Bmat, Umat).multiply(Bmat) + np.dot(Umat, Bmat).multiply(Bmat)
        return c + c.T
    elif ID == 'M4':
        c = np.dot(Bmat, Bmat).multiply(Bmat)
        return c
    elif ID == 'M5':
        c = np.dot(Umat, Umat).multiply(Umat) + np.dot(Umat, Umat.T).multiply(Umat) + np.dot(Umat.T, Umat).multiply(Umat)
        return c + c.T
    elif ID == 'M6':
        c = np.dot(Umat, Bmat).multiply(Umat) + np.dot(Bmat, Umat.T).multiply(Umat.T) + np.dot(Umat.T, Umat).multiply(Bmat)
        return c
    elif ID == 'M7':
        c = np.dot(Umat.T, Bmat).multiply(Umat.T) + np.dot(Bmat, Umat).multiply(Umat) + np.dot(Umat, Umat.T).multiply(Bmat)
        return c


def personalized_pagerank_kernel(adj_mat, param_alpha=0.05, eps_tol=0.5):
    """Compute an approximate personalized pagerank kernel [1]_ . 
    
    If a is the regularization parameter, computes (I - (1 - param_alpha)*gmat )^{-1} using power iterations 
    (as in https://arxiv.org/pdf/1911.05485.pdf and https://arxiv.org/pdf/1810.05997.pdf ). 

    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph.
    param_alpha : float, optional
        The regularization parameter. Default is 0.05.
    eps_tol : float, optional
        The tolerance for the power iteration. Default is 0.5.
    
    Returns
    -------
    W : sparse matrix
        The personalized pagerank kernel matrix.
    
    References
    ----------
    .. [1] J. Klicpera, A. Bojchevski, S. Günnemann, Predict then propagate: 
           graph neural networks meet personalized pagerank, 
           arXiv preprint arXiv:1810.05997, 2018.
    """
    stop_crit = False
    R = compute_diffusion_kernel(adj_mat, alpha=0.0, sym=False, normalize=True).T
    labeled_signal = scipy.sparse.identity(R.shape[0])
    F = scipy.sparse.identity(R.shape[0])
    sparsemats = True
    while not stop_crit:
        if sparsemats:
            F_new = ((1-param_alpha)*R.dot(F)) + (param_alpha*labeled_signal)
            resid = (F_new - F)
            resid_err = np.sum(np.square(resid.data))
            rel_err = resid_err/np.sum(np.square(F_new.data))
        else:
            F_new = np.array(((1-param_alpha)*R.dot(F)) + (param_alpha*labeled_signal))
            rel_err = np.square(F_new - F).sum()/np.square(F_new).sum()
        F = F_new
        print(resid_err, rel_err)
        if rel_err <= eps_tol:
            stop_crit = True
    return F


def gcn_kernel(adj_mat, self_loops=True):
    """Compute a graph convolutional net kernel.

    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph.
    self_loops : bool, optional
        Whether to add self-loops to the graph. Default is True.
    
    Returns
    -------
    norm_kernel : sparse matrix
        The GCN kernel computed from the input graph.
    """
    if self_loops:
        adj_mat = adj_mat + scipy.sparse.identity(adj_mat.shape[0])
    norm_kernel = compute_diffusion_kernel(adj_mat, alpha=0.0, sym=True, normalize=True)
    return norm_kernel


def diffusion_mutualreach_kernel(adj_mat, diffusion_steps=1):
    """Given a graph, compute a kernel indicating nodes that are mutually reachable after diffusion.

    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph.
    diffusion_steps : int, optional
        The number of diffusion steps to use. Default is 1.
    
    Returns
    -------
    result : sparse matrix
        The mutual reachability kernel.
    """
    powers_so_far = []
    kmat = adj_mat
    powers_so_far.append(kmat)
    for i in range(diffusion_steps-1):
        kmat = kmat.dot(adj_mat)
        powers_so_far.append(kmat)
    result = reduce(lambda x,y:x+y, powers_so_far)
    return result.multiply(result.T)


def mst_connections_kernel(adj_mat, distance_mat=None):
    """Given a graph, compute a kernel corresponding to its minimum spanning tree.

    The MST is weighted by the Euclidean distances between nodes.
    If the graph is directed, the kernel is computed on an undirected version of the graph.
    
    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph. Can be weighted or unweighted.
    distance_mat : sparse matrix, optional
        Distance matrix of the graph.
    
    Returns
    -------
    treemat : sparse matrix
        Adjacency matrix of the minimum spanning tree of the graph.
    """
    # Symmetrize graph, with connections for k-neighborhood relationships in either direction. 
    # A no-op for undirected unweighted graphs.
    umat = adj_mat + adj_mat.T - adj_mat.multiply(adj_mat.T)
    umat.data = np.ones_like(umat.data)
    
    if distance_mat is not None:
        umat = umat.multiply(distance_mat)
    treemat = scipy.sparse.csgraph.minimum_spanning_tree(umat)
    return treemat


def saul_nonparametric_kernel(adj_mat, diffusion_steps=1):
    """Compute the nonparametric kernel from [1]_ .
    
    Parameters
    ----------
    adj_mat : sparse matrix
        Adjacency matrix of the graph.
    diffusion_steps : int, optional
        The number of diffusion steps to use. Default is 1.
    
    Returns
    -------
    result : sparse matrix
        The nonparametric kernel.
    
    References
    ----------
    .. [1] Lawrence K. Saul, A tractable latent variable model 
           for nonlinear dimensionality reduction, Proceedings of the 
           National Academy of Sciences 117, no. 27 (2020): 15403-15408.
    """
    Mmat = diffusion_mutualreach_kernel(adj_mat, diffusion_steps=diffusion_steps)
    Tmat = mst_connections_kernel(adj_mat)
    return adj_mat.multiply(Mmat + Tmat)

