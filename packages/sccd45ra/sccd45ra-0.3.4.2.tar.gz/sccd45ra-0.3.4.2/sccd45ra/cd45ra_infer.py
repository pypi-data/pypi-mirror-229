import scanpy as sc
import numpy as np
import pandas as pd
from joblib import dump, load
import pkg_resources

def cd45ra_infer(adata, inplace = True):
    
    print("This function takes normalized, log transformed input")
    _adata_df = pd.DataFrame(adata.X.A, index = adata.obs_names, columns = adata.var_names)
    _model_path = pkg_resources.resource_filename('sccd45ra', 'model/best_rbf_svm.joblib')
    _model = load(_model_path)
    _feature_path= pkg_resources.resource_filename('sccd45ra', 'feature/Supplement Tables.xlsx')
    _best_rbf_svm_features = pd.read_excel(_feature_path, sheet_name = 'S3')['RBF SVM'].dropna()
    _org_df = pd.DataFrame(index = adata.obs_names, columns = _best_rbf_svm_features)
    for i in _best_rbf_svm_features:
        if i in adata.var_names:
            # Check if it's a sparse matrix
            if isinstance(adata.X, sp.sparse.spmatrix):
                _org_df[i] = adata.X[:, adata.var_names == i].A
            else:
                _org_df[i] = adata.X[:, adata.var_names == i]
        else:
            _org_df[i] = np.zeros([adata.shape[0], 1])
    
    
    if inplace == True:
        adata.obs['CD45RA_predict'] = _model.predict(_org_df)
        adata.obs['CD45RA_predict'] = adata.obs['CD45RA_predict'].astype(str)
    else:
        _prediction = _model.predict(_org_df)
        return _prediction