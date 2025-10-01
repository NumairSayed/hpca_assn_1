#!/bin/bash

# --- Configuration ---
# This script will compile the benchmark, run it for a range of graph sizes,
# and then plot the performance results using Python.

# Compile the project first
echo "Compiling the benchmark program..."
make

# Set the name of your BFS executable file.
BENCHMARK_EXE="./bfs"

# Set the range for the '-g' parameter (e.g., 2 to 25)
START_G=2
END_G=25

# Output file names
DATA_FILE="bfs_performance_data.csv"
PLOT_FILE="bfs_performance_graph.png"


# --- Dependency Installation ---
echo "Checking and installing dependencies (pandas, matplotlib)..."
# Update package list and install Python3 and pip if they are not present

# Install required Python libraries using pip
pip3 install pandas matplotlib


# --- Pre-run Checks ---
# Check if the benchmark executable exists and is executable
if [ ! -x "$BENCHMARK_EXE" ]; then
    echo "Error: Benchmark executable '$BENCHMARK_EXE' not found or is not executable."
    echo "This might have happened if the 'make' command failed."
    exit 1
fi


# --- Main Script Logic ---
echo "Starting BFS benchmark process..."

# Create a temporary CSV file and add the header row
echo "g_value,num_vertices,undirected_edges,avg_time,teps" > "$DATA_FILE"

# Loop through the specified range of -g values
for g in $(seq "$START_G" "$END_G"); do
    echo "Running benchmark with -g $g..."

    # Run the benchmark command and capture its output
    # The '|| true' prevents the script from exiting if the benchmark fails for one run
    output=$($BENCHMARK_EXE -g "$g -n 1 -l" || true)

    # Use grep and awk to parse the relevant lines from the output
    edges=$(echo "$output" | grep 'undirected edges' | awk '{print $6}')
    avg_time=$(echo "$output" | grep 'Average Time:' | awk '{print $3}')
    echo edges: $edges, avg_time: $avg_time
    # Ensure we got valid numbers before proceeding
    if [[ -z "$edges" || -z "$avg_time" ]]; then
        echo "Warning: Could not parse output for -g $g. Skipping."
        continue
    fi

    # Calculate the number of vertices (2^g)
    num_vertices=$((2**g))

    # Calculate TEPS (Traversed Edges Per Second) using 'bc' for floating point math
    # Handles the case where avg_time might be zero to prevent division by zero error
    teps=$(echo "scale=4; if ($avg_time > 0) $edges / $avg_time else 0" | bc)

    # Append the collected data to our CSV file
    echo "$g,$num_vertices,$edges,$avg_time,$teps" >> "$DATA_FILE"
done

echo "Benchmark data collection complete. Generating graph with Python..."


# --- Graph Generation using Python ---
# Use a 'here document' (<<EOF) to pass a Python script to the interpreter.
# This script reads the CSV and generates a plot similar to the example.
python3 <<EOF
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Define file paths from the bash script's variables
data_file = "$DATA_FILE"
plot_file = "$PLOT_FILE"

try:
    # Read the generated CSV data into a pandas DataFrame
    df = pd.read_csv(data_file)

    # Create a plot with a specific figure size for better readability
    plt.figure(figsize=(10, 6))

    # Plot 'num_vertices' on the x-axis and 'teps' on the y-axis
    plt.plot(df['num_vertices'], df['teps'], marker='o', linestyle='-', label='BFS Performance')

    # Set both axes to a logarithmic scale
    plt.xscale('log', base=10)
    plt.yscale('log', base=10)

    # Set the title and labels for the graph
    plt.title('BFS Performance Scaling', fontsize=16)
    plt.xlabel('Number of Nodes (Log Scale)', fontsize=12)
    plt.ylabel('Traversed Edges Per Second (TEPS) (Log Scale)', fontsize=12)

    # Add a grid to the plot for easier analysis
    plt.grid(True, which="both", linestyle='--', linewidth=0.5)

    # Display the legend
    plt.legend()

    # Save the plot to the specified image file
    plt.savefig(plot_file)

    print(f"Successfully generated plot and saved to {plot_file}")

except FileNotFoundError:
    print(f"Error: The data file '{data_file}' was not found.", file=sys.stderr)
except Exception as e:
    print(f"An error occurred during plot generation: {e}", file=sys.stderr)

EOF

# --- Cleanup ---
# Remove the temporary data file after the graph is created
rm "$DATA_FILE"

echo "Graph generation complete! Plot saved as '$PLOT_FILE'."

