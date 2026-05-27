import matplotlib.pyplot as plt
from data_preprocessing import extract_and_format_data, extract_river_data, filter_quality_flags

# 1. Extract the data (Note: using '../sample_data/' since the script is inside the 'src/' folder

raw_nodes, raw_reaches = extract_and_format_data('./sample_data/')

# 2. Clean the data using our auto-detecting quality filter
clean_nodes = filter_quality_flags(raw_nodes)
clean_reaches = filter_quality_flags(raw_reaches)

# 3. Isolate the target river
ganga_nodes = extract_river_data(clean_nodes, target_river='Ganga')

# --- PLOTTING ---
fig, ax = plt.subplots(1, 2, figsize=(20, 8))

# Plot 1: All SWOT Nodes and Reaches
if clean_reaches is not None and not clean_reaches.empty:
    clean_reaches.plot(ax=ax[0], color='blue', linewidth=0.5, alpha=0.6, label='Reaches')
if clean_nodes is not None and not clean_nodes.empty:
    clean_nodes.plot(ax=ax[0], color='red', markersize=1, alpha=0.5, label='Nodes')
    
ax[0].set_title('All SWOT Nodes and Reaches', fontsize=14, fontweight='bold')
ax[0].set_axis_off()

# Plot 2: Isolated Ganga River Segment
if ganga_nodes is not None and not ganga_nodes.empty:
    ganga_nodes.plot(ax=ax[1], color='green', markersize=5, label='Ganga Nodes')
    ax[1].set_title('Isolated Ganga River Segment', fontsize=14, fontweight='bold')
else:
    # If the sample data doesn't contain the Ganga river, display a fallback message
    ax[1].set_title('Ganga River Not Found in Sample Data', fontsize=14, fontweight='bold')
    ax[1].text(0.5, 0.5, 'No Data to Plot', horizontalalignment='center', verticalalignment='center', fontsize=12)
    
ax[1].set_axis_off()

plt.tight_layout()
plt.show()