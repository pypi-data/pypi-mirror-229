import numpy as np, scipy
import requests, os
import scanpy as sc


def get_gtex_snrnaseq(
    file_path='GTEx_8_snRNAseq_atlas.h5ad', 
    mode='all', 
    num_subsample=None, 
    random_state=42
):
    """Download and load the GTEx snRNA-seq atlas [1]_. 

    Parameters
    ----------
    file_path : str, optional
        Path to save the file to. 
    mode : str, optional
        One of ``['all', 'immune']``. Default: ``'all'``.
    num_subsample : int, optional
        Number of cells to subsample. Default: ``None``.
    random_state : int, optional
    
    Returns
    -------
    adata : AnnData
        The GTEx snRNA-seq atlas.
    """
    if not os.path.exists(file_path):
        if mode=='immune':
            fname = 'GTEx_8_tissues_snRNAseq_immune_atlas_071421.public_obs.h5ad'
        elif mode=='all':
            fname = 'GTEx_8_tissues_snRNAseq_atlas_071421.public_obs.h5ad'
        else:
            raise ValueError('mode must be "immune" or "all"')
        url_str = f'https://storage.googleapis.com/gtex_analysis_v9/snrna_seq_data/{fname}'
        response = requests.get(url_str)
        with open(file_path, 'wb') as fp:
            fp.write(response.content)
    adata = sc.read(file_path)
    if num_subsample is not None:
        adata = sc.pp.subsample(adata, n_obs=int(num_subsample), random_state=random_state, copy=True)
    return adata