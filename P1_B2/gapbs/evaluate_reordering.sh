#!/bin/bash

# Parameters
MAX_SCALE=25
RUNS=100
CSV_FILE="bfs_benchmark.csv"
PLOT_FILE="bfs_runtime_vs_vertices.png"

# Ensure requirements are installed
echo "Installing Python requirements..."
pip3 install -q numpy matplotlib pandas

# Initialize CSV file
echo "n_vertices,avg_unordered_time,avg_reordered_time" > $CSV_FILE

## ensure binaries are built 
make 

# Helper: current time in microseconds
time_us() {
    python3 - <<'EOF'
import time
print(int(time.time() * 1_000_000))
EOF
}

# BFS runner
run_bfs() {
    local graph=$1
    local runs=$2
    local outfile=$3
    rm -f "$outfile"
    for i in $(seq 1 $runs); do
        SRC=$(( RANDOM ))
        START=$(time_us)
        ./bfs -f "$graph" -s $SRC >/dev/null 2>&1
        END=$(time_us)
        ELAPSED=$(( END - START ))
        echo "$ELAPSED" >> "$outfile"
    done
}

# Compute mean from txt file
mean_runtime() {
    python3 - <<EOF
import numpy as np
with open("$1") as f:
    vals = [int(x.strip()) for x in f if x.strip()]
print(np.mean(vals) if vals else 0)
EOF
}

# Keep track of all temporary txt files
TEMP_FILES=()

# Main loop over scales
for SCALE in $(seq 1 $MAX_SCALE); do
    N_VERTICES=$(( 2 ** SCALE ))
    UNORDERED="unordered_${SCALE}.sg"
    REORDERED="reordered_${SCALE}.sg"
    TIMES_UNORDERED="times_unordered_${SCALE}.txt"
    TIMES_REORDERED="times_reordered_${SCALE}.txt"

    TEMP_FILES+=("$TIMES_UNORDERED" "$TIMES_REORDERED")

    echo "Generating unordered graph 2^$SCALE ..."
    ./converter -g $SCALE -b $UNORDERED

    echo "Creating reordered graph 2^$SCALE ..."
    ./converter -g $SCALE -b $REORDERED -r

    echo "Running BFS on unordered graph ..."
    run_bfs "$UNORDERED" $RUNS "$TIMES_UNORDERED"

    echo "Running BFS on reordered graph ..."
    run_bfs "$REORDERED" $RUNS "$TIMES_REORDERED"

    # Compute averages
    AVG_UNORDERED=$(mean_runtime "$TIMES_UNORDERED")
    AVG_REORDERED=$(mean_runtime "$TIMES_REORDERED")

    # Append to CSV
    echo "$N_VERTICES,$AVG_UNORDERED,$AVG_REORDERED" >> $CSV_FILE

    # Delete graph files to save space
    rm -f $UNORDERED $REORDERED
done

# Delete all temporary txt files
rm -f "${TEMP_FILES[@]}"

echo "Benchmark complete. Results saved in $CSV_FILE"

# ---- PLOTTING SECTION ----
echo "Generating plot..."
python3 - <<EOF
import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "$CSV_FILE"
df = pd.read_csv(CSV_FILE)

n_vertices = df['n_vertices']
avg_unordered = df['avg_unordered_time']
avg_reordered = df['avg_reordered_time']

plt.figure(figsize=(10, 6))
plt.plot(n_vertices, avg_unordered, marker='o', label='Unordered Graph')
plt.plot(n_vertices, avg_reordered, marker='s', label='Reordered Graph')

plt.xlabel("Number of Vertices (log2 scale)")
plt.ylabel("Average BFS Time (µs)")
plt.title("BFS Average Runtime vs Graph Size")
plt.xscale('log', base=2)
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend()

max_vertex = n_vertices.iloc[-1]
plt.annotate(f"{avg_unordered.iloc[-1]:.0f} µs",
             xy=(max_vertex, avg_unordered.iloc[-1]),
             xytext=(10, 0), textcoords='offset points')
plt.annotate(f"{avg_reordered.iloc[-1]:.0f} µs",
             xy=(max_vertex, avg_reordered.iloc[-1]),
             xytext=(10, -15), textcoords='offset points')

plt.tight_layout()
plt.savefig("$PLOT_FILE", dpi=300)
print(f"Plot saved as {PLOT_FILE}")
EOF
