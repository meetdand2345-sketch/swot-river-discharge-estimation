import numpy as np

def calculate_node_dxa(wse: np.ndarray, width: np.ndarray) -> np.ndarray:
    """
    Calculates the cumulative change in cross-sectional area (d_x_area) for nodes over time.
    Reconstructs the missing SWOT variable using a 2D Matrix Trapezoidal Rule (Time x Space).
    """
    # Change in height and average width between consecutive time steps
    dh = wse[1:, :] - wse[:-1, :]
    w_avg = (width[1:, :] + width[:-1, :]) / 2.0
    
    # Incremental change in area
    dA_step = w_avg * dh
    
    # Cumulative sum over time to track total anomaly from the first observation
    dA_cumulative = np.cumsum(dA_step, axis=0)
    
    # Initialize matrix base state (t=0) with zeros
    initial_state = np.zeros((1, wse.shape[1]))
    d_x_area_nodes = np.vstack([initial_state, dA_cumulative])
    
    return d_x_area_nodes

def calculate_manning_discharge(n: float, A0: np.ndarray, d_x_area: np.ndarray, width: np.ndarray, slope: np.ndarray) -> np.ndarray:
    """
    Calculates river discharge time-series using the modified Manning's equation 
    with a wide-channel approximation.
    """
    # MCMC Math Safeties: Prevent Negative Slopes and Zero-Width division
    S_safe = np.maximum(slope, 1e-6)
    W_safe = np.maximum(width, 1e-2)
    
    total_area = np.maximum(A0 + d_x_area, 1e-2)
    
    Q = (1.0 / n) * (total_area ** (5/3)) * (W_safe ** (-2/3)) * (S_safe ** (1/2))
    
    return Q