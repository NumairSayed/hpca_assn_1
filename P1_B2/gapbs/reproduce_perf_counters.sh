#!/bin/bash
set -e

GRAPH_FILE="25.sg"

# 1. Generate graph
echo "[INFO] Generating graph ${GRAPH_FILE}..."
./converter -g 25 -b $GRAPH_FILE

# 2. Define counters dictionary
declare -A COUNTERS
COUNTERS["L1_I_misses"]="L1-icache-load-misses l1-icache-load-misses icache.misses cpu/L1-icache-load-misses/"
COUNTERS["L1_D_misses"]="l1_data_cache_fills_all cpu/l1_data_cache_fills_all/ ls_dc_accesses"
COUNTERS["L2_misses"]="l2_cache_req_stat.ic_dc_miss_in_l2 cpu/l2_cache_req_stat.ic_dc_miss_in_l2/ l2_dcache_load_misses l2-dcache-load-misses"
COUNTERS["L3_misses"]="ls_dmnd_fills_from_sys.mem_io_local ls_dmnd_fills_from_sys.int_cache LLC-load-misses llc-load-misses"
COUNTERS["D_TLB_misses"]="l1_dtlb_misses cpu/l1_dtlb_misses/ ls_l1_d_tlb_miss.all"
COUNTERS["Branch_mispred"]="branch-misses branch_misses cpu/branch-misses/"
COUNTERS["FLOPs"]="fp_ret_sse_avx_ops.all fp_arith_inst_retired.scalar_double fp"

# 3. Pick working counter names
SELECTED_EVENTS=()
for key in "${!COUNTERS[@]}"; do
    for event in ${COUNTERS[$key]}; do
        if perf list | grep -qw "$event"; then
            echo "[INFO] Using $event for $key"
            SELECTED_EVENTS+=("$event")
            break
        fi
    done
done

# Join events with commas
EVENTS=$(IFS=, ; echo "${SELECTED_EVENTS[*]}")

# 4. Run perf with selected counters
echo "[INFO] Running perf stat on BFS..."
perf stat -e $EVENTS ./bfs -f $GRAPH_FILE -n 1 -l

# 5. Cleanup
echo "[INFO] Removing generated graph ${GRAPH_FILE}..."
rm -f $GRAPH_FILE
