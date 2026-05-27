import numpy as np
from src.data_preprocessing import extract_and_format_data, extract_river_data, filter_quality_flags
from src.feature_engineering import extract_hydrological_features
from src.metroman_prep import generate_metroman_matrices
from src.sword_api import fetch_sword_priors
from mannings import calculate_node_dxa
from src.metroman import MetroMan

def run_pipeline():
    print("=== 1. STARTING SWOT PIPELINE ===")
    data_path = './sample_data/'
    raw_nodes, raw_reaches = extract_and_format_data(data_path)
    
    if raw_nodes is None or raw_nodes.empty:
        print("CRITICAL ERROR: No data found.")
        return

    print("\n=== 2. RUNNING QUALITY CONTROL ===")
    clean_nodes = filter_quality_flags(raw_nodes)
    clean_reaches = filter_quality_flags(raw_reaches)
    
    print("\n=== 3. EXTRACTING TARGET RIVER ===")
    ganga_nodes = extract_river_data(clean_nodes, target_river='Ganga')
    ganga_reaches = extract_river_data(clean_reaches, target_river='Ganga')
    
    print("\n=== 4. FEATURE ENGINEERING ===")
    model_nodes, model_reaches = extract_hydrological_features(ganga_nodes, ganga_reaches)
    
    print("\n=== 5. MATRIX GENERATION ===")
    metroman_input_reaches = generate_metroman_matrices(model_reaches)
    metroman_input_nodes = generate_metroman_matrices(model_nodes)
    
    w_matrix_r = metroman_input_reaches['width']
    s_matrix_r = metroman_input_reaches['slope']
    dxa_matrix_r = metroman_input_reaches['d_x_area'] 
    times = metroman_input_reaches['times']
    reach_ids = metroman_input_reaches['spatial_ids']
    print("\n=== 6. FETCHING SWORD PRIORS (LOCAL CACHE) ===")
    SWORD_FILE = "as_sword_v17.nc" 

    n_priors, A0_priors, n_stds, A0_stds = [], [], [], []
    for r_id in reach_ids:
        # Notice we removed KAGGLE_DATASET from the function arguments here
        n, A0, n_s, A0_s = fetch_sword_priors(SWORD_FILE, int(r_id))
        n_priors.append(n)
        A0_priors.append(A0)
        n_stds.append(n_s)
        A0_stds.append(A0_s)

    if None in A0_priors:
        print("Optimization aborted due to missing SWORD priors.")
        return
        
    A0_prior_arr = np.array(A0_priors)
    global_n_prior = np.mean(n_priors)
    global_n_std = np.mean(n_stds)
    global_A0_std = np.mean(A0_stds)
    
    # Dynamic temporal calculation (converts dt to seconds)
    time_gaps = times[1:] - times[:-1]
    actual_dt_seconds = np.mean(time_gaps)

    print("\n=== 7A. REACH-LEVEL METROMAN OPTIMIZATION ===")
    reach_optimizer = MetroMan(n_prior=global_n_prior, A0_prior=A0_prior_arr, n_std=global_n_std, A0_std=global_A0_std)
    
    final_Q_reaches, _, _ = reach_optimizer.metropolis_sampler(
        d_x_area=dxa_matrix_r, width=w_matrix_r, slope=s_matrix_r, dt=actual_dt_seconds, iterations=5000
    )

    print("\n=== 7B. NODE-LEVEL METROMAN PREP & OPTIMIZATION ===")
    w_matrix_n = metroman_input_nodes['width']
    wse_matrix_n = metroman_input_nodes['wse']
    s_matrix_n = metroman_input_nodes['slope'] 
    node_ids = metroman_input_nodes['spatial_ids']
    
    # 2D Trapezoidal Reconstruction for Nodes
    dxa_matrix_n = calculate_node_dxa(wse_matrix_n, w_matrix_n)
    
    # Prior Broadcasting Mapping
    node_reach_mapping = model_nodes[['node_id', 'reach_id']].drop_duplicates().set_index('node_id')['reach_id'].to_dict()
    reach_prior_mapping = dict(zip(reach_ids, A0_priors)) 
    
    node_A0_priors = [reach_prior_mapping.get(node_reach_mapping.get(n_id), np.mean(A0_priors)) for n_id in node_ids]
    node_A0_prior_arr = np.array(node_A0_priors)
    
    node_optimizer = MetroMan(n_prior=global_n_prior, A0_prior=node_A0_prior_arr, n_std=global_n_std, A0_std=global_A0_std)
    
    final_Q_nodes, _, _ = node_optimizer.metropolis_sampler(
        d_x_area=dxa_matrix_n, width=w_matrix_n, slope=s_matrix_n, dt=actual_dt_seconds, iterations=5000
    )
    
    print("\n=== PIPELINE COMPLETE ===")
    print(f"Reach Q Matrix Shape: {final_Q_reaches.shape}")
    print(f"Node Q Matrix Shape:  {final_Q_nodes.shape}")

if __name__ == "__main__":
    run_pipeline()