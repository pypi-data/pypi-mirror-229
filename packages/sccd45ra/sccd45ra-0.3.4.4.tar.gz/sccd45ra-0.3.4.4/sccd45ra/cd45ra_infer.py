import scanpy as sc
import numpy as np
import pandas as pd
from joblib import dump, load
import pkg_resources
import scipy as sp

def cd45ra_infer(adata, inplace = True):
    
    print("This function takes normalized, log transformed input")
        # Load features
    _model_path = pkg_resources.resource_filename('sccd45ra', 'model/best_rbf_svm.joblib')
    _model = load(_model_path)
    _feature_path = pkg_resources.resource_filename('sccd45ra', 'feature/Supplement Tables.xlsx')
    _best_rbf_svm_features = pd.read_excel(_feature_path, sheet_name='S3')['RBF SVM'].dropna()
    
    # Create a dataframe to store the required feature data
    _org_df = pd.DataFrame(index=adata.obs_names, columns=_best_rbf_svm_features)
    
    for feature in _best_rbf_svm_features:
        if feature in adata.var_names:
            # Get column values, taking care of sparse data
            column_data = adata.X[:, adata.var_names == feature].A if isinstance(adata.X, sp.sparse.spmatrix) else adata.X[:, adata.var_names == feature]
            
            # Since column_data might have more than 1 dimension, we need to squeeze it to match _org_df shape
            _org_df[feature] = np.squeeze(column_data)
        else:
            _org_df[feature] = 0  # This will broadcast the assignment across all rows
            
    if inplace == True:
        adata.obs['CD45RA_predict'] = _model.predict(_org_df)
        adata.obs['CD45RA_predict'] = adata.obs['CD45RA_predict'].astype(str)
    else:
        _prediction = _model.predict(_org_df)
        return _prediction