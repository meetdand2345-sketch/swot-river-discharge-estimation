import pandas as pd
import numpy as np
from typing import Dict, Any

def generate_metroman_matrices(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    id_col = 'node_id' if 'node_id' in df.columns else 'reach_id'

    # Pivot strictly on structural pass ID to avoid sparse matrix explosions
    width_df = df.pivot_table(index='folder_source', columns=id_col, values='width', aggfunc='mean')
    
    # Prioritize smoothed WSE for nodes if available for spatial stability
    wse_col = 'wse_sm' if 'wse_sm' in df.columns else 'wse'
    wse_df = df.pivot_table(index='folder_source', columns=id_col, values=wse_col, aggfunc='mean')
    
    slope_col = 'slope' if 'slope' in df.columns else 'slope (from reach)'
    slope_df = df.pivot_table(index='folder_source', columns=id_col, values=slope_col, aggfunc='mean')

    # Extract exact chronological timestamps to compute dt
    time_df = df.pivot_table(index='folder_source', columns=id_col, values='time', aggfunc='mean')
    mean_pass_times = time_df.mean(axis=1).values  

    matrices = {
        'passes': width_df.index.values,      
        'times': mean_pass_times,             
        'spatial_ids': width_df.columns.values, 
        'width': width_df.values,             
        'wse': wse_df.values,                 
        'slope': slope_df.values              
    }
    
    # Check for Reach-exclusive variables
    if 'd_x_area' in df.columns:
        matrices['d_x_area'] = df.pivot_table(index='folder_source', columns=id_col, values='d_x_area', aggfunc='mean').values

    return matrices