## To generate .txt files for counter values for each rodinia benchmark:

*NOTE*: Make sure the data is present in the gpu-rodinia/data.

```bash
cd ./gpu-rodinia/openmp

./backprop 33554432 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> backprop_perf.txt; wait $pid

./bfs 4 ../../data/bfs/graph1MW_6.txt & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> bfs_perf.txt; wait $pid

./euler3d_cpu ../../data/cfd/missile.domn.0.2M & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> euler3d_cpu_perf.txt; wait $pid

./euler3d_cpu_double ../../data/cfd/missile.domn.0.2M & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> euler3d_cpu_double_perf.txt; wait $pid

./hotspot 1024 1024 2 4 ../../data/hotspot/temp_1024 ../../data/hotspot/power_1024 output.out & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> hotspot_perf.txt; wait $pid

./kmeans_serial/kmeans -i ../../data/kmeans/kdd_cup & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> kmeans_serial_perf.txt; wait $pid

./kmeans_openmp/kmeans -n 4 -i ../../data/kmeans/kdd_cup & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> kmeans_openmp_perf.txt; wait $pid

./lavaMD -cores 4 -boxes1d 20 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> lavaMD_perf.txt; wait $pid

./omp/lud_omp -s 8000 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> lud_omp_perf.txt; wait $pid

./needle 2048 10 2 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> needle_perf.txt; wait $pid

./nn filelist_4 5 30 90 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> nn_perf.txt; wait $pid

./particle_filter -x 128 -y 128 -z 10 -np 10000 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> particle_filter_perf.txt; wait $pid

./pathfinder 100000 100 > out & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> pathfinder_perf.txt; wait $pid

./pre_euler3d_cpu ../../data/cfd/missile.domn.0.2M & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> pre_euler3d_cpu_perf.txt; wait $pid

./pre_euler3d_cpu_double ../../data/cfd/missile.domn.0.2M & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> pre_euler3d_cpu_double_perf.txt; wait $pid

./srad_v2 2048 2048 0 127 0 127 2 0.5 2 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> srad_v2_perf.txt; wait $pid

./srad_v1 100 0.5 502 458 4 & pid=$!; perf stat -p $pid -e cycles,instructions,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all -I 10 2> srad_v1_perf.txt; wait $pid

```

## To combine the .txt files to csv for rodinia files

```bash
cd ./predataset/rodinia_shard
pip install -r requirements.txt
python make_dataset.py
```
This will generate a file named rodinia_combined_perf.csv

## To make cpi characteristics plot for rodinia:

```bash
cd ./predataset/rodinia_shard
python viz.py
```

## To regress this data 
```bash
python regress.py combined_perf.csv
```

## Repeat the same for gabps 
