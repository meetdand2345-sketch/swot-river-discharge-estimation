import os
import geopandas as gpd
import pandas as pd
from typing import Tuple, Optional

def extract_and_format_data(data_dir: str = '../sample_data/') -> Tuple[Optional[gpd.GeoDataFrame], Optional[gpd.GeoDataFrame]]:
    nodes_list = []
    reaches_list = []
    print(f"Starting data extraction from {data_dir}...")

    for dirname, _, filenames in os.walk(data_dir):
        for filename in filenames:
            if filename.endswith('.shp'):
                file_path = os.path.join(dirname, filename)
                try:
                    gdf = gpd.read_file(file_path)
                    gdf['folder_source'] = os.path.basename(dirname) # Crucial for later merge
                    
                    if '_Node_' in filename:
                        nodes_list.append(gdf)
                    elif '_Reach_' in filename:
                        reaches_list.append(gdf)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    nodes_df = gpd.GeoDataFrame(pd.concat(nodes_list, ignore_index=True)) if nodes_list else None
    reaches_df = gpd.GeoDataFrame(pd.concat(reaches_list, ignore_index=True)) if reaches_list else None

    # Cast to 64-bit integers to prevent ID corruption
    if nodes_df is not None:
        nodes_df['node_id'] = nodes_df['node_id'].astype('int64')
        nodes_df['reach_id'] = nodes_df['reach_id'].astype('int64')
        
    if reaches_df is not None:
        reaches_df['reach_id'] = reaches_df['reach_id'].astype('int64')

    return nodes_df, reaches_df

def extract_river_data(nodes_df: gpd.GeoDataFrame, target_river: str = 'Ganga') -> gpd.GeoDataFrame:
    river_nodes = nodes_df[nodes_df['river_name'] == target_river].copy()
    return river_nodes

def filter_quality_flags(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if 'node_q' in df.columns:
        flag_col = 'node_q'
    elif 'reach_q' in df.columns:
        flag_col = 'reach_q'
    else:
        return df
        
    return df[df[flag_col].isin([0, 1])].copy()