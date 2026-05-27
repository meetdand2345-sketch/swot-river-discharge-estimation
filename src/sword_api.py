import os
import numpy as np
import netCDF4 as nc

def fetch_sword_priors(filename: str, reach_id: int, save_dir: str = './sample_data/sword_cache'):
    """
    Reads SWORD priors directly from a local cached NetCDF file.
    Zero API dependencies!
    """
    file_path = os.path.join(save_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"  [!] Missing file: {file_path}")
        print(f"  [!] Please place the downloaded {filename} into the {save_dir} directory.")
        return None, None, None, None
        
    try:
        dataset = nc.Dataset(file_path, 'r')
        reach_ids_array = dataset.variables['reach_id'][:]
        idx = np.where(reach_ids_array == reach_id)[0]
        
        if len(idx) == 0:
            dataset.close()
            return None, None, None, None
            
        idx = idx[0]
        # Validated against SWORD standard variable names
        n_prior = float(dataset.variables['n'][idx])       
        A0_prior = float(dataset.variables['a0'][idx])     
        n_std = float(dataset.variables['n_u'][idx])       
        A0_std = float(dataset.variables['a0_u'][idx])     
        
        dataset.close()
        return n_prior, A0_prior, n_std, A0_std
        
    except Exception as e:
        print(f"  [!] Error reading NetCDF: {e}")
        return None, None, None, None