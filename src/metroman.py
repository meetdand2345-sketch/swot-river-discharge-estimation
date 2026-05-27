import numpy as np
from src.mannings import calculate_manning_discharge

class MetroMan:
    def __init__(self, n_prior: float, A0_prior: np.ndarray, n_std: float, A0_std: float):
        self.n_prior = n_prior
        self.A0_prior = A0_prior  
        self.n_std = n_std
        self.A0_std = A0_std

    def error_function(self, Q: np.ndarray, dA: np.ndarray, dt: float) -> float:
        # Conservation of Mass: dQ/dx + dA/dt = 0
        dA_dt = (dA[1:, :] - dA[:-1, :]) / dt
        
        # Time-centering Q to prevent numerical instability
        Q_avg_t = (Q[1:, :] + Q[:-1, :]) / 2.0
        dQ_dx = Q_avg_t[:, 1:] - Q_avg_t[:, :-1]
        
        theta = dQ_dx + dA_dt[:, :-1]
        return np.sum(theta ** 2)

    def metropolis_sampler(self, d_x_area: np.ndarray, width: np.ndarray, slope: np.ndarray, dt: float, iterations: int = 5000):
        current_n = self.n_prior
        current_A0 = np.copy(self.A0_prior)
        
        current_Q = calculate_manning_discharge(current_n, current_A0, d_x_area, width, slope)
        current_error = self.error_function(current_Q, d_x_area, dt)
        
        best_n = current_n
        best_A0 = np.copy(current_A0)
        min_error = current_error
        
        for i in range(iterations):
            proposed_n = np.abs(np.random.normal(current_n, self.n_std))
            proposed_A0 = np.abs(np.random.normal(current_A0, self.A0_std))
            
            proposed_Q = calculate_manning_discharge(proposed_n, proposed_A0, d_x_area, width, slope)
            proposed_error = self.error_function(proposed_Q, d_x_area, dt)
            
            acceptance_ratio = np.exp(-0.5 * (proposed_error - current_error))
            
            if np.random.rand() < acceptance_ratio:
                current_n = proposed_n
                current_A0 = proposed_A0
                current_error = proposed_error
                
                if current_error < min_error:
                    best_n = current_n
                    best_A0 = np.copy(current_A0)
                    min_error = current_error
                    
        final_Q = calculate_manning_discharge(best_n, best_A0, d_x_area, width, slope)
        return final_Q, best_n, best_A0