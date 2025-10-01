#!/bin/bash
# run_matmul_perf.sh
# Run all matrix multiplication functions and save perf stats in separate files

TARGET=./matmul
BLOCK_SIZE=64
RESULTS_DIR=./reports
# List of normal matrix multiplication functions
# normal_funcs=("matmul_ijk" "matmul_jik" "matmul_kij" "matmul_ikj" "matmul_jki" "matmul_kji")

# List of tiled matrix multiplication functions
tiled_funcs=("matmul_tiled_ijk" "matmul_tiled_ikj" "matmul_tiled_jik" "matmul_tiled_jki" "matmul_tiled_kij" "matmul_tiled_kji")
# tiled_funcs=("matmul_tiled_ikj")
# Make sure target is compiled
make

echo "Running normal matrix multiplication variants..."
for func in "${normal_funcs[@]}"; do
    echo "Running $func..."
    taskset -c 0 perf stat -e fp_ret_sse_avx_ops.all,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch $TARGET "$func" 2> "${RESULTS_DIR}/${func}.txt"
    echo "$func done, output saved to ${func}.txt"
done

echo "Running tiled matrix multiplication variants (block size $BLOCK_SIZE)..."
for func in "${tiled_funcs[@]}"; do
    echo "Running $func..."
    taskset -c 0 perf stat -e fp_ret_sse_avx_ops.all,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch $TARGET "$func" "$BLOCK_SIZE" 2> "${RESULTS_DIR}/${func}.txt"
    echo "$func done, output saved to ./reports/${func}.txt"
done
echo "All runs completed."
