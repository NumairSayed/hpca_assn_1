import pandas as pd
import matplotlib.pyplot as plt

# File path of the combined CSV
CSV_FILE = "rodinia_combined_perf.csv"

# List of relevant columns
CYCLES_COL = "cycles"
INSTR_COL = "instructions"

# Read the CSV
df = pd.read_csv(CSV_FILE, index_col="Index")

# Ensure numeric
df[CYCLES_COL] = pd.to_numeric(df[CYCLES_COL], errors="coerce")
df[INSTR_COL] = pd.to_numeric(df[INSTR_COL], errors="coerce")
df["time"] = pd.to_numeric(df["time"], errors="coerce")

# Calculate IPC = instructions / cycles
df["IPC"] = df[INSTR_COL] / df[CYCLES_COL]

# Plot
plt.figure(figsize=(12,6))
plt.plot(df["time"], df["IPC"], marker='o', linestyle='-', color='b')
plt.xlabel("Time (s)")
plt.ylabel("IPC (Instructions per Cycle)")
plt.title("Time vs IPC")
plt.grid(True)
plt.tight_layout()
plt.show()
