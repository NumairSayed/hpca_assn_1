#!/bin/bash
OUTFILE="backprop_perf.csv"

# Events list
EVENTS="cycles,inst_retired.any,branch-misses,ls_dc_accesses,l1_data_cache_fills_all,l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2,ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch,fp_ret_sse_avx_ops.all"

# Start benchmark in background
./backprop 33554432 &
pid=$!

# Run perf stat with 10ms sampling and redirect output to CSV
perf stat -p $pid -e $EVENTS -I 10 --log-fd 1 2>&1 \
  | awk -v OFS=',' '
    /^[ ]*[0-9]/ {
        gsub(",","",$1)
        val[$2]=$1
        next
    }
    END {
        cpi = (val["inst_retired.any"] > 0 ? val["cycles"]/val["inst_retired.any"] : 0)
        print "binary","cycles","instructions","branch-misses","L1","L2","ITLB","L1I","L2I","LLC","DRAM","FLOPs","CPI" > "'"$OUTFILE"'"
        print "backprop", val["cycles"], val["inst_retired.any"], val["branch-misses"], \
              val["ls_dc_accesses"]+val["l1_data_cache_fills_all"], \
              val["l2_cache_req_stat.ic_access_in_l2"]+val["l2_cache_req_stat.ic_dc_hit_in_l2"]+val["l2_cache_req_stat.ic_dc_miss_in_l2"], \
              0,0,0, \
              val["ls_dmnd_fills_from_sys.int_cache"]+val["ls_dmnd_fills_from_sys.mem_io_local"], \
              val["ls_dmnd_fills_from_sys.mem_io_local"]+val["ls_dispatch.ld_dispatch"], \
              val["fp_ret_sse_avx_ops.all"], cpi >> "'"$OUTFILE"'"
    }
  '

wait $pid
echo "Perf results saved to $OUTFILE"
