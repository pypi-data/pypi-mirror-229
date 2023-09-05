import numpy as np, scipy
from scipy.sparse import csr_array


def calc_over_edges(graph_in, data_in_values, dist_fn=None):
    """Calculate given pairwise similarity kernel over a given subset of edges.

    Parameters
    ----------
    graph_in : sparse matrix
        (n x n) adjacency matrix of graph
    data_in_values : ndarray
        (n x d) matrix of data values at each vertex
    dist_fn : function, optional
        Function to compute distance between two data points. Default: Euclidean distance.
    
    Returns
    -------
    gg : sparse matrix
        (n x n) matrix of pairwise similarities between pairs of edge-adjacent data points.
    """
    gg = np.zeros_like(graph_in.toarray())
    nnzlist = list(zip(*np.nonzero(graph_in.toarray())))
    for i in range(len(nnzlist)):
        d = nnzlist[i]
        if dist_fn is None:
            gg[d] = np.exp(-np.sum(np.square(data_in_values[d[0],:] - data_in_values[d[1],:])))
        else:
            gg[d] = dist_fn(data_in_values[d[0],:], data_in_values[d[1],:])
    return scipy.sparse.csr_matrix(gg)


def intrinsic_dim_MLE(
    weighted_kNN_graph, k, 
    impute_1nn=False, bias_correction=True, eps=1e-5
):
    """
    Returns MLE estimator of local intrinsic dimension at each data point. 
    Distribution of points is modeled as a Poisson process, i.e. with axioms: 
    (1) Nonoverlapping regions are independent, 
    (2) Prob of event is proportional to interval size, 
    (3) <=1 event occurs in any atomic interval.
    Closed under thinning, mapping, and displacement (by transition matrix). 
    """
    idim_fn = np.zeros(weighted_kNN_graph.shape[0])
    if issparse(weighted_kNN_graph):
        g = weighted_kNN_graph.toarray()
    else:
        g = weighted_kNN_graph
    idim_fn = np.zeros(g.shape[0])
    for i in range(g.shape[0]):
        knn_dists = np.sort(g[i,:])[-1:-(k+1):-1]
        r = np.log(-(np.log(knn_dists) + eps))
        if impute_1nn:    # If the similarity to the most similar point is already 1, pretend it's as similar as the 2nd most
            r[0] = r[1]
        idim_fn[i] = 1.0/np.mean(r[-1] - r)
    if bias_correction:
        idim_fn = idim_fn*((k-2)/(k-1))
    return idim_fn