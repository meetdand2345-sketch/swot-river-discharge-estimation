import numpy as np
import geopandas as gpd
from typing import Tuple

def extract_hydrological_features(nodes_df: gpd.GeoDataFrame, reaches_df: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    nodes_df.columns = nodes_df.columns.str.lower().str.strip()
    reaches_df.columns = reaches_df.columns.str.lower().str.strip()
    
    # Purge SWOT fill values before they corrupt matrix math
    nodes_df.replace(-999999999999.0, np.nan, inplace=True)
    reaches_df.replace(-999999999999.0, np.nan, inplace=True)
    
    # Target variables including smoothed WSE (wse_sm) for nodes
    target_node_cols = ['node_id', 'reach_id', 'time', 'lon', 'lat', 'width', 'wse', 'wse_sm', 'folder_source', 'geometry']
    target_reach_cols = ['reach_id', 'time', 'p_lon', 'p_lat', 'width', 'wse', 'slope', 'slope2', 'd_x_area', 'folder_source', 'geometry']
    
    actual_node_cols = [col for col in target_node_cols if col in nodes_df.columns]
    actual_reach_cols = [col for col in target_reach_cols if col in reaches_df.columns]
    
    feature_nodes = nodes_df[actual_node_cols].copy()
    feature_reaches = reaches_df[actual_reach_cols].copy()
    
    # Spatiotemporal Merge: Broadcast Reach Slopes down to constituent Nodes
    merge_cols = [col for col in ['slope', 'slope2'] if col in actual_reach_cols]
    
    if merge_cols and 'reach_id' in actual_node_cols and 'folder_source' in actual_node_cols:
        reach_slopes = feature_reaches[['reach_id', 'folder_source'] + merge_cols].copy()
        
        # Merge on BOTH spatial location (reach_id) and exact satellite overpass (folder_source)
        feature_nodes = feature_nodes.merge(reach_slopes, on=['reach_id', 'folder_source'], how='left')
        
    return feature_nodes, feature_reaches