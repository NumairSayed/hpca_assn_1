import pandas as pd
import glob
import os
import json

# List of events we want as columns
EVENTS = [
    "cycles",
    "instructions",
    "branch-misses",
    "ls_dc_accesses",
    "l1_data_cache_fills_all",
    "l2_cache_req_stat.ic_access_in_l2",
    "l2_cache_req_stat.ic_dc_hit_in_l2",
    "l2_cache_req_stat.ic_dc_miss_in_l2",
    "ls_dmnd_fills_from_sys.int_cache",
    "ls_dmnd_fills_from_sys.mem_io_local",
    "ls_dispatch.ld_dispatch",
    "fp_ret_sse_avx_ops.all"
]

def parse_perf_file(filepath):
    """
    Parse a single perf txt file and return a dataframe.
    Each timestamp has multiple rows; we pivot them to columns by event name.
    """
    data = []
    with open(filepath, "r") as f:
        lines = f.readlines()

    current_time = None
    current_row = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            time = float(parts[0])
            count = int(parts[1].replace(",", ""))
            event = parts[2]
        except ValueError:
            continue

        if current_time is None:
            current_time = time

        if time != current_time:
            # finish previous timestamp
            data.append(current_row)
            current_row = {}
            current_time = time

        current_row["time"] = time
        current_row[event] = count

    if current_row:
        data.append(current_row)

    df = pd.DataFrame(data)
    # Fill missing events with 0
    for event in EVENTS:
        if event not in df.columns:
            df[event] = 0

    # Keep only desired columns
    df = df[["time"] + EVENTS]
    return df

def merge_contiguous(df, instr_threshold=100_000_000):
    """
    Merge consecutive rows with instructions < threshold until the cumulative
    instructions exceed the threshold.
    """
    merged_rows = []
    temp = None

    for idx, row in df.iterrows():
        if temp is None:
            temp = row.copy()
        else:
            # accumulate counts
            temp[EVENTS] = temp[EVENTS] + row[EVENTS]
            temp["time"] = row["time"]  # take the latest timestamp

        if temp["instructions"] >= instr_threshold:
            merged_rows.append(temp.copy())
            temp = None

    # add any leftover temp if it passed threshold
    if temp is not None and temp["instructions"] >= instr_threshold:
        merged_rows.append(temp.copy())

    merged_df = pd.DataFrame(merged_rows)
    merged_df.reset_index(drop=True, inplace=True)
    return merged_df

def process_all_files(file_pattern="*_perf.txt", instr_threshold=100_000_000):
    files = sorted(glob.glob(file_pattern), key=os.path.getctime)
    combined_df = pd.DataFrame()
    for f in files:
        print(f"Processing {f} ...")
        df = parse_perf_file(f)
        df = merge_contiguous(df, instr_threshold)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

def save_outputs(df, csv_file="combined_perf.csv", json_file="combined_perf.json"):
    df.to_csv(csv_file, index_label="Index")
    df.to_json(json_file, orient="records", indent=2)

if __name__ == "__main__":
    combined_df = process_all_files(file_pattern="*_perf.txt", instr_threshold=100_000_000)
    save_outputs(combined_df)
    print(f"Done! CSV and JSON saved. Total rows: {len(combined_df)}")
