"""
Implements hyperbolic diffusion map embedding. 
Code from https://github.com/Ya-Wei0/HyperbolicDiffusionDistance , accessed 6/3/23. 
Paper: https://arxiv.org/abs/2305.18962
"""


"""
MIT License

Copyright (c) 2023 Ya-Wei0

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import numpy as np, scipy
from sklearn.metrics import pairwise_distances
from scipy.sparse.linalg import eigs
from scipy.sparse.linalg import eigsh
from scipy import linalg


TOL = 1e-6


def diffusion_operator_normalized_data(data, dis_mat, affinity = None, sigma = 2, 
                                    num_ev = 20, if_full_spec = False):
    
    if dis_mat is None:
        dis_mat = pairwise_distances(data)

    if affinity is None:
        Gaussian_kernel = np.exp(-dis_mat / sigma)
    else:
        print('there is affinity matrix')
        Gaussian_kernel = affinity

    d = 1 / np.sum(Gaussian_kernel, axis=1)
    K = np.diag(d) @ Gaussian_kernel @ np.diag(d)

    d_ = np.diag(1 / np.sqrt(np.sum(K, axis=1)))
    d__ = np.diag(np.sqrt(np.sum(K, axis=1)))
    M = d_ @ K @ d_
    
    if if_full_spec:
        ev, evv = linalg.eigh(M)
    else:
        ev, evv = eigsh(M, k=num_ev, which='LM')

    evv = evv[:, np.argsort(ev)[::-1]]
    ev = (np.sort(ev)[::-1])
    ev = np.where(ev>TOL, ev, TOL)

    left_evv  = d_ @ evv
    right_evv = evv.T @ d__

    return ev, left_evv, right_evv


def diffusion_operator_graph(affinity, num_ev = 20, if_normalized = False, if_full_spec = False):
    
    D = np.diag(affinity.sum(axis = 1))
    L = D - affinity

    if if_normalized:
        d_ = np.diag(1 / np.sqrt(np.sum(affinity, axis=1)))
        L  = d_ @ L @ d_
    
    if if_full_spec:
        ev, evv = linalg.eigh(L)
    else:
        ev, evv = eigsh(L, k=num_ev, which='SM')

    ev = np.exp(-ev)        
    left_evv  = evv 
    right_evv = evv 

    return ev, left_evv, right_evv


def hyp_dis(x,y):
    return 2 * np.arcsinh(np.linalg.norm(x-y)/(2*np.sqrt(x[-1]*y[-1])))


def hyperbolic_diffusion(ev, left_evv, right_evv, K):

    X_hat, hdd = [], [], []
    single_mat = []
    time_step = 1/np.power(2, np.arange(K))
    weight    = 2/np.power(2, np.arange(K)/2)

    for ii in range(len(time_step)):
        evv_power = np.power(ev, time_step[ii])

        x_hat = (left_evv @ np.diag(evv_power) @ right_evv)
        x_hat = np.sqrt(np.where(x_hat>TOL, x_hat, TOL))
   
        single_mat.append((2 * np.arcsinh( weight[ii] * pairwise_distances(x_hat))))
        
        tmp = np.concatenate((x_hat, (1/(2*weight[ii])) * np.ones((left_evv.shape[0], 1))), axis = 1)
        X_hat.append(tmp)

    hdd = np.sum(single_mat, axis = 0)
    
    return X_hat, hdd