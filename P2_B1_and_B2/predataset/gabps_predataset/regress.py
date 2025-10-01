import sys
import os
import json
import time
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats

# Try to import sklearn's LinearRegression with positive constraint; if not available, fallback to lsq_linear
try:
    from sklearn.linear_model import LinearRegression
    SKL_LINREG_POSITIVE = True
except Exception:
    SKL_LINREG_POSITIVE = False

from scipy.optimize import lsq_linear

# ---------- CONFIG ----------
RANDOM_STATE = 42
TEST_SIZE = 0.2   # 80/20 train/val

# Mapping of conceptual features to a list of possible CSV column names (tries in order)
FEATURE_COLUMN_CANDIDATES = {
    "L1_I_misses": [
        "L1-icache-load-misses", "l1-icache-load-misses", "icache.misses",
        "L1-icache-load-misses_OR_cpu/L1-icache-load-misses/"  # sometimes weird entries; fallback
    ],
    "L1_D_misses": [
        "l1_data_cache_fills_all", "l1_data_cache_fills_all_OR_cpu/l1_data_cache_fills_all/",
        "ls_dc_accesses", "ls_dc_accesses"   # note: ls_dc_accesses sometimes counts accesses, not misses; we include as fallback
    ],
    "L2_misses": [
        "l2_cache_req_stat.ic_dc_miss_in_l2",
        "l2_cache_req_stat.ic_dc_miss_in_l2_OR_cpu/l2_cache_req_stat.ic_dc_miss_in_l2/",
        "l2_dcache_load_misses", "l2-dcache-load-misses"
    ],
    "L3_misses": [
        # L3 demand fills (mem_io_local) and dispatch combine to DRAM traffic; treat as L3/DRAM proxy
        "ls_dmnd_fills_from_sys.mem_io_local", "ls_dmnd_fills_from_sys.int_cache",
        "LLC-load-misses", "llc-load-misses"
    ],
    "D_TLB_misses": [
        "l1_dtlb_misses", "l1_dtlb_misses_OR_cpu/l1_dtlb_misses/", "ls_l1_d_tlb_miss.all"
    ],
    "Branch_mispred": [
        "branch-misses", "branch_misses", "branch-misses_OR_cpu/branch-misses/"
    ],
    # optionally include FLOPs as a feature to explain CPI (should be small for BFS but useful for compute-heavy)
    "FLOPs": [
        "fp_ret_sse_avx_ops.all", "fp_arith_inst_retired.scalar_double", "fp"
    ]
}

# Column names we expect / will compute
CYCLES_COL = "cycles"
INSTR_COL = "instructions"
TIME_COL = "time"  # If present; else we will use row index

# ---------- helpers ----------

def find_column(df, candidate_names):
    """Return the first column in df.columns that matches any of candidate_names (case-sensitive or fuzzy)."""
    cols = list(df.columns)
    for cand in candidate_names:
        # direct match
        if cand in cols:
            return cand
        # try case-insensitive match and ignoring non-alnum
        for c in cols:
            if ''.join(filter(str.isalnum, c.lower())) == ''.join(filter(str.isalnum, cand.lower())):
                return c
    return None

def build_feature_matrix(df):
    """
    Build X (features) and feature_names from dataframe using FEATURE_COLUMN_CANDIDATES.
    If none of the candidate names are found for a feature, fill that column with zeros and warn.
    """
    X_cols = []
    feature_names = []
    missing = []
    for feat, candidates in FEATURE_COLUMN_CANDIDATES.items():
        col = find_column(df, candidates)
        if col is not None:
            X_cols.append(df[col].astype(float).fillna(0).values)
            feature_names.append(feat)
        else:
            # not found -> zero column (but still keep as feature so coefficients map)
            X_cols.append(np.zeros(len(df), dtype=float))
            feature_names.append(feat)
            missing.append(feat)
    X = np.vstack(X_cols).T  # shape (n_samples, n_features)
    return X, feature_names, missing

def compute_metrics(y_true, y_pred, p):
    """
    Compute RMSE, R2, adjusted R2, residuals, F-stat, p-value.
    p = number of predictors (not counting intercept)
    """
    n = len(y_true)
    residuals = y_true - y_pred
    SSE = np.sum(residuals**2)
    SST = np.sum((y_true - np.mean(y_true))**2)
    SSR = SST - SSE
    R2 = 1.0 - (SSE/SST) if SST > 0 else 0.0
    RMSE = np.sqrt(SSE / n)
    adjR2 = 1.0 - (1.0 - R2) * (n - 1) / max(n - p - 1, 1)

    # F-statistic: (SSR/p) / (SSE/(n-p-1))
    denom = (SSE / max(n - p - 1, 1))
    num = SSR / max(p, 1)
    F = (num / denom) if denom > 0 else np.nan
    # p-value from F-distribution:
    if not np.isnan(F):
        p_value = 1.0 - stats.f.cdf(F, p, max(n - p - 1, 1))
    else:
        p_value = np.nan

    return {
        "RMSE": float(RMSE),
        "R2": float(R2),
        "adjR2": float(adjR2),
        "SSE": float(SSE),
        "SST": float(SST),
        "SSR": float(SSR),
        "F": float(F) if not np.isnan(F) else None,
        "F_pvalue": float(p_value) if not np.isnan(p_value) else None,
        "residuals": residuals
    }

# ---------- main ----------
def main(csv_path):
    if not os.path.exists(csv_path):
        print("CSV file not found:", csv_path)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print("Loaded CSV with columns:", df.columns.tolist())

    # Ensure cycles & instructions exist
    if CYCLES_COL not in df.columns or INSTR_COL not in df.columns:
        raise RuntimeError(f"CSV must contain '{CYCLES_COL}' and '{INSTR_COL}' columns")

    # Compute target CPI = cycles / instructions (avoid divide by zero)
    df["CPI"] = df[CYCLES_COL].astype(float) / df[INSTR_COL].astype(float).replace({0: np.nan})
    df = df.dropna(subset=["CPI"]).reset_index(drop=True)
    n_samples = len(df)
    print(f"Samples after dropping NaN CPI: {n_samples}")

    # Build features matrix X
    X, feature_names, missing_features = build_feature_matrix(df)
    if missing_features:
        print("WARNING: Some conceptual features not found in CSV. These will be zero columns:", missing_features)
    print("Feature names used (in order):", feature_names)

    # Keep time (if present) or use index as time
    time_col = np.arange(len(df))
    df["__time_for_plot__"] = time_col

    # Split train / validation
    X_train, X_val, y_train, y_val, time_train, time_val, idx_train, idx_val = train_test_split(
        X, df["CPI"].values, df["__time_for_plot__"].values, df.index.values,
        test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"Train samples: {len(X_train)}, Validation samples: {len(X_val)}")

    # Fit non-negative regression: try sklearn LinearRegression(positive=True) first
    coef = None
    intercept = 0.0
    success = False
    if SKL_LINREG_POSITIVE:
        try:
            print("Trying sklearn.linear_model.LinearRegression(positive=True)...")
            lr = LinearRegression(positive=True, fit_intercept=True)
            lr.fit(X_train, y_train)
            coef = lr.coef_.copy()
            intercept = float(lr.intercept_)
            success = True
            print("sklearn LinearRegression(positive=True) succeeded.")
        except Exception as e:
            print("sklearn positive LinearRegression failed:", e)
            success = False

    if not success:
        # fallback: use lsq_linear to solve min ||Xb + c - y|| with b >= 0 (non-negative),
        # we will include intercept by augmenting X with a column of ones and allowing intercept unconstrained by splitting approach:
        # Approach: center y and X? Simpler: treat intercept separately: subtract mean of y and not constrain intercept:
        # We'll fit b >=0 for y' = y - mean(y), and include intercept = mean(y) - mean(X)*b
        print("Falling back to scipy.optimize.lsq_linear (non-negative bounds).")
        # center y and X to improve stability
        y_train_mean = np.mean(y_train)
        y_train_centered = y_train - y_train_mean
        # center columns of X
        X_means = X_train.mean(axis=0)
        Xc = X_train - X_means
        # solve min ||Xc * b - y_centered|| subject to b >= 0
        res = lsq_linear(Xc, y_train_centered, bounds=(0, np.inf), method='trf', verbose=1)
        coef = res.x
        intercept = float(y_train_mean - np.dot(X_means, coef))
        print("lsq_linear result success:", res.success)
        print("res.status:", res.status)

    coef = np.array(coef, dtype=float)
    print("Intercept:", intercept)
    print("Coefficients (non-negative):")
    for name, c in zip(feature_names, coef):
        print(f"  {name}: {c:.6g}")

    # Predictions on validation set
    y_pred = X_val.dot(coef) + intercept
    y_train_pred = X_train.dot(coef) + intercept

    # Metrics on validation set
    p = X.shape[1]  # number of predictors
    metrics = compute_metrics(y_val, y_pred, p)

    # Residuals series for test set
    residuals = metrics["residuals"]
    df_res = pd.DataFrame({
        "index": idx_val,
        "time": time_val,
        "y_true": y_val,
        "y_pred": y_pred,
        "residual": residuals
    }).sort_values("index").reset_index(drop=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    residuals_file = f"residuals_{timestamp}.csv"
    df_res.to_csv(residuals_file, index=False)
    print("Residuals saved to:", residuals_file)

    # Save metrics
    metrics_out = {
        "n_train": int(len(X_train)),
        "n_val": int(len(X_val)),
        "features": feature_names,
        "intercept": float(intercept),
        "coefficients": {name: float(c) for name, c in zip(feature_names, coef)},
        "RMSE": metrics["RMSE"],
        "R2": metrics["R2"],
        "adjR2": metrics["adjR2"],
        "SSE": metrics["SSE"],
        "SSR": metrics["SSR"],
        "SST": metrics["SST"],
        "F": metrics["F"],
        "F_pvalue": metrics["F_pvalue"]
    }
    metrics_file = f"regression_metrics_{timestamp}.json"
    with open(metrics_file, "w") as fh:
        json.dump(metrics_out, fh, indent=2)
    print("Metrics saved to:", metrics_file)

    # Plot: time vs CPI (actual and predicted) for validation set
    plt.figure(figsize=(12,6))
    # sort by time for plotting
    order = np.argsort(time_val)
    plt.plot(np.array(time_val)[order], y_val[order], label="CPI (actual)", marker='o', linestyle='-', markersize=4)
    plt.plot(np.array(time_val)[order], y_pred[order], label="CPI (predicted)", marker='x', linestyle='--', markersize=4)
    plt.xlabel("time (s) or index (if no time column)")
    plt.ylabel("CPI (cycles/instruction)")
    plt.title("Validation: CPI actual vs predicted")
    plt.legend()
    plt.grid(True)
    plot_file = f"pred_vs_actual_{timestamp}.png"
    plt.tight_layout()
    plt.savefig(plot_file, dpi=200)
    print("Plot saved to:", plot_file)

    # Print summary
    print("\n===== SUMMARY =====")
    print("Train size:", len(X_train))
    print("Val size:", len(X_val))
    print("RMSE:", metrics["RMSE"])
    print("R2:", metrics["R2"])
    print("Adjusted R2:", metrics["adjR2"])
    print("F-statistic:", metrics["F"], "p-value:", metrics["F_pvalue"])
    print("Residuals saved at:", residuals_file)
    print("Metrics JSON:", metrics_file)
    print("Plot:", plot_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 regress_cpi.py combined_perf.csv")
        sys.exit(1)
    csv_path = sys.argv[1]
    main(csv_path)
