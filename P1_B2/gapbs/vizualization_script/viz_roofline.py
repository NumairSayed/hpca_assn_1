import numpy as np
import matplotlib.pyplot as plt

# --- Input Data from perf output ---
edges = 523609147
traversal_time = 1.22865  # seconds
cache_line_size = 64  # bytes

# Performance counters
ls_dc_accesses = 2063199297           # L1 data cache accesses
l2_hits = 63798690                   # L2 hits
l2_misses = 151495204                # L2 misses

# --- Calculations ---

# 1. Operational Intensity (OI) - Edges per Byte from DRAM
# Based on the user's direction, DRAM traffic is proxied by L2 misses.
bytes_from_dram = l2_misses * cache_line_size
operational_intensity = edges / bytes_from_dram

# 2. Performance (TEPS - Traversed Edges Per Second)
teps = edges / traversal_time

# 3. Achieved Bandwidths (Bytes/Second) calculated from counters
# These values determine the slopes of the roofs.
achieved_l1_bw = (ls_dc_accesses * cache_line_size) / traversal_time
achieved_l2_bw = ((l2_hits + l2_misses) * cache_line_size) / traversal_time
# Using L2 misses as a proxy for traffic to L3 and DRAM
achieved_l3_dram_bw = (l2_misses * cache_line_size) / traversal_time

# 4. Peak TEPS roof (given by user)
teps_roof = 5.2 * 10**8

# --- Plotting ---

# Create a range for Operational Intensity (x-axis)
oi_range = np.logspace(-3, 2, 200)

# Calculate the performance ceilings for each roof
l1_roof_perf = achieved_l1_bw * oi_range
l2_roof_perf = achieved_l2_bw * oi_range
dram_roof_perf = achieved_l3_dram_bw * oi_range

# Create the plot
plt.figure(figsize=(12, 8))
plt.style.use('seaborn-v0_8-whitegrid')

# Plot the memory bandwidth roofs based on ACHIEVED bandwidth
plt.plot(oi_range, l1_roof_perf, color='green', linestyle=':', label=f'Achieved L1 BW Roof ({achieved_l1_bw/1e9:.2f} GB/s)')
plt.plot(oi_range, l2_roof_perf, color='orange', linestyle=':', label=f'Achieved L2 BW Roof ({achieved_l2_bw/1e9:.2f} GB/s)')
plt.plot(oi_range, dram_roof_perf, color='purple', linestyle='-', label=f'Achieved L3/DRAM BW Roof ({achieved_l3_dram_bw/1e9:.2f} GB/s)', lw=2)

# Plot the horizontal TEPS roof
plt.axhline(y=teps_roof, color='red', linestyle='--', label=f'Peak TEPS Roof ({teps_roof/1e8:.2f} x 10^8 TEPS)')

# Plot the application's performance point
plt.plot(operational_intensity, teps, 'o', markersize=12, color='blue', label=f'Application Performance')

# Annotate the performance point
plt.annotate(f'OI: {operational_intensity:.3f}\nTEPS: {teps/1e8:.2f} x 10^8',
             xy=(operational_intensity, teps),
             xytext=(operational_intensity * 0.2, teps * 1.5),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
             fontsize=10)

# Formatting
plt.xscale('log')
plt.yscale('log')
plt.title('Roofline Model based on Achieved Bandwidths', fontsize=16)
plt.xlabel('Operational Intensity (Edges / Byte)', fontsize=12)
plt.ylabel('Performance (TEPS)', fontsize=12)
plt.grid(True, which="both", ls="--")

# Set plot limits to focus on the relevant area
plt.xlim(1e-3, 1e2)
plt.ylim(1e8, 1e9)

plt.legend()
plt.tight_layout()

# Save the plot
plt.savefig('roofline_plot_achieved_bw.png')

print("Corrected roofline plot generated and saved as 'roofline_plot_achieved_bw.png'")
print(f"\nCalculated Operational Intensity: {operational_intensity:.4f} Edges/Byte")
print(f"Calculated Performance: {teps/1e8:.4f} x 10^8 TEPS")
print(f"Achieved L1 Bandwidth: {achieved_l1_bw/1e9:.2f} GB/s")
print(f"Achieved L2 Bandwidth: {achieved_l2_bw/1e9:.2f} GB/s")
print(f"Achieved L3/DRAM Bandwidth: {achieved_l3_dram_bw/1e9:.2f} GB/s")
