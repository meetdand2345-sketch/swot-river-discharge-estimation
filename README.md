# swot-river-discharge-estimation

A robust, high-performance Python pipeline for estimating river discharge using SWOT Level 2 High Rate River Single Pass (L2_HR_RiverSP) vector products.

## Overview
This repository provides a modular data processing pipeline designed to convert SWOT satellite shapefiles into river discharge estimates. The project implements a dual-routing approach, performing mass-conserved flow law inversion at both the Reach and Node scales.

## Key Features
- **Spatiotemporal Matrix Assembly**: Converts flat SWOT shapefiles into aligned `Time x Space` matrices, specifically engineered to avoid the temporal aliasing traps inherent in high-rate SWOT data.
- **Dual-Routing Architecture**: 
  - **Reach-Level**: Uses pre-computed `d_x_area` for mass-conserved flow inversion.
  - **Node-Level**: Employs manual trapezoidal integration for cross-sectional area reconstruction at 200m spatial resolution.
- **Physics-Based Optimization**: Implements the Metropolis-Manning (MetroMan) algorithm to stochastically optimize flow-law parameters ($n$ and $A_0$).
- **Robust Quality Control**: Implements rigorous filtering based on SWOT L2 quality flags and handles satellite-specific "no-data" fill values (-999999999999.0).
- **Offline-Ready**: Features a local caching strategy that bypasses external API dependencies during runtime, ensuring stable and reproducible results.

## Methodology
This pipeline follows the theoretical framework established for the SWOT mission. It leverages the Prior River Database (PRD) for physical constraints and utilizes Manning's Equation for discharge inversion.

## Installation
1. Clone the repository: 
   `git clone https://github.com/meetdand2345-sketch/swot-river-discharge-estimation.git`
2. Install requirements: 
   `pip install -r requirements.txt`
3. Place your SWOT shapefiles in `./sample_data/` and your SWORD NetCDF file in `./data/sword_cache/`.

## Quick Start
Execute the entire pipeline by running the orchestrator from the root directory:
```bash
python main.py

## References
SWOT Product Description Document: Level 2 KaRIn High Rate River Single Pass Vector (L2_HR_RiverSP) Data Product, 2025.

Altenau et al., (2021) The Surface Water and Ocean Topography (SWOT) Mission River Database (SWORD): A Global River Network for Satellite Data Products. Water Resources Research.
