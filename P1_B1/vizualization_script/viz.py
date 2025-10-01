import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D # <--- FIX: Added the missing import here!

# --- 1. HARDWARE PARAMETERS (The Roof) ---
PEAK_GFLOPS = 116.4  # Peak DP FLOPS for AMD Ryzen 7 7435HS
DRAM_BW_GBs = 50.0   # Estimated DRAM Bandwidth
L3_BW_GBs = 200.0    # Estimated L3 Bandwidth
L2_BW_GBs = 400.0    # Estimated L2 Bandwidth
L1_BW_GBs = 900.0    # Estimated L1 Bandwidth

# --- 2. MEASURED DATA POINTS (The Performance) ---
# Organized for easy iteration
data_points = [
    {'label': 'i,j,k (S)', 'oi': 0.026, 'perf': 0.116, 'color': 'red', 'marker': 'o'},
    {'label': 'i,j,k (T)', 'oi': 48.278, 'perf': 0.717, 'color': 'red', 'marker': 's'},
    {'label': 'i,k,j (S)', 'oi': 1.600, 'perf': 6.208, 'color': 'blue', 'marker': 'o'},
    {'label': 'i,k,j (T)', 'oi': 28.455, 'perf': 14.354, 'color': 'blue', 'marker': 's'},
    {'label': 'j,i,k (S)', 'oi': 0.044, 'perf': 0.178, 'color': 'green', 'marker': 'o'},
    {'label': 'j,i,k (T)', 'oi': 15.867, 'perf': 0.702, 'color': 'green', 'marker': 's'},
    {'label': 'j,k,i (S)', 'oi': 0.026, 'perf': 0.070, 'color': 'purple', 'marker': 'o'},
    {'label': 'j,k,i (T)', 'oi': 0.070, 'perf': 0.117, 'color': 'purple', 'marker': 's'},
    {'label': 'k,i,j (S)', 'oi': 1.082, 'perf': 3.164, 'color': 'orange', 'marker': 'o'},
    {'label': 'k,i,j (T)', 'oi': 4.448, 'perf': 13.308, 'color': 'orange', 'marker': 's'},
    {'label': 'k,j,i (S)', 'oi': 0.022, 'perf': 0.066, 'color': 'brown', 'marker': 'o'},
    {'label': 'k,j,i (T)', 'oi': 0.057, 'perf': 0.114, 'color': 'brown', 'marker': 's'},
]

# --- 3. PLOTTING FUNCTION ---
def plot_full_roofline():
    """Generates the comprehensive Roofline Model plot."""
    OI = np.logspace(-2.5, 3, 500) # OI from ~0.003 to 1000

    plt.figure(figsize=(14, 9))
    ax = plt.gca()

    def get_performance(OI, BW):
        return np.minimum(PEAK_GFLOPS, OI * BW)

    # 4. Plot Roofline Ceilings
    # Note: Use brighter/thicker lines for the ceilings
    ax.loglog(OI, get_performance(OI, DRAM_BW_GBs), label=f'DRAM BW ({DRAM_BW_GBs:.0f} GB/s)', color='#00aaff', linestyle='--', linewidth=2)
    ax.loglog(OI, get_performance(OI, L3_BW_GBs), label=f'L3 BW ({L3_BW_GBs:.0f} GB/s)', color='#ff7700', linestyle='--', linewidth=2)
    ax.loglog(OI, get_performance(OI, L2_BW_GBs), label=f'L2 BW ({L2_BW_GBs:.0f} GB/s)', color='#00cc00', linestyle='--', linewidth=2)
    ax.loglog(OI, get_performance(OI, L1_BW_GBs), label=f'L1 BW ({L1_BW_GBs:.0f} GB/s)', color='#cc00cc', linestyle='--', linewidth=2)

    # Peak Performance (Horizontal Line)
    ax.axhline(y=PEAK_GFLOPS, color='k', linestyle='-', linewidth=3, label=f'Peak FLOPS ({PEAK_GFLOPS:.1f} GFLOPS)')

    # 5. Plot Measured Data Points

    for data in data_points:
        # Plot the point
        ax.plot(data['oi'], data['perf'],
                marker=data['marker'], markersize=10, color=data['color'],
                linestyle='', markeredgecolor='k', zorder=5)

        # Annotate the point (only label the non-worst performers for clarity)
        if data['perf'] > 0.5 or data['label'] in ['i,j,k (S)', 'k,j,i (S)']:
             ax.annotate(data['label'], (data['oi'], data['perf']),
                        textcoords="offset points", xytext=(5,5), ha='left', fontsize=8, color='k')


    # 6. Final Plot Aesthetics
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Operational Intensity (FLOPs/Byte)', fontsize=14)
    ax.set_ylabel('Performance (GFLOPS/sec)', fontsize=14)
    ax.set_title(f'Comprehensive Roofline Model for MM on AMD Ryzen 7 7435HS', fontsize=16)
    ax.grid(True, which="both", ls="--", linewidth=0.5, alpha=0.6)

    # Set limits based on data
    ax.set_xlim(5e-3, 1e3) # Set x-limit to 0.005 to 1000
    ax.set_ylim(5e-2, 1.5e2) # Set y-limit to 0.05 to 100

    # Custom legend

    # Create legend handles for point type (Optimization Type)
    point_legend_handles = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='k', markeredgecolor='k', markersize=10, label='Simple Version'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='k', markeredgecolor='k', markersize=10, label='Tiled Version'),
    ]

    # Create legend handles for ceiling lines (Hardware Ceilings)
    ceiling_legend_handles = ax.lines

    # Create legend handles for color-coding the patterns (Loop Order Pattern)
    color_legend_handles = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markeredgecolor='k', markersize=10, label='i,j,k Pattern'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markeredgecolor='k', markersize=10, label='i,k,j Pattern'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markeredgecolor='k', markersize=10, label='j,i,k Pattern'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markeredgecolor='k', markersize=10, label='j,k,i Pattern'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markeredgecolor='k', markersize=10, label='k,i,j Pattern'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='brown', markeredgecolor='k', markersize=10, label='k,j,i Pattern'),
    ]

    # Combine all legends using the manual method to place them precisely
    first_legend = ax.legend(handles=point_legend_handles, loc='upper left', title="Optimization Type", fontsize=10)
    ax.add_artist(first_legend)

    second_legend = ax.legend(handles=ceiling_legend_handles, loc='lower right', title="Hardware Ceilings", fontsize=10)
    ax.add_artist(second_legend)

    third_legend = ax.legend(handles=color_legend_handles, loc='upper right', title="Loop Order Pattern", fontsize=10)

    plt.show()

# Execute the plotting function
plot_full_roofline()