CC = gcc
CFLAGS = -O3 -march=native -fno-openmp 
TARGET = matmul

# FLOPs (SSE/AVX)
FLOP_EVENTS = fp_ret_sse_avx_ops.all

# L1 data cache
L1_EVENTS = ls_dc_accesses,l1_data_cache_fills_all

# L2 cache
L2_EVENTS = l2_cache_req_stat.ic_access_in_l2,l2_cache_req_stat.ic_dc_hit_in_l2,l2_cache_req_stat.ic_dc_miss_in_l2

# L3 cache
L3_EVENTS = ls_dmnd_fills_from_sys.int_cache,ls_dmnd_fills_from_sys.mem_io_local

# DRAM / memory controller
DRAM_EVENTS = ls_dmnd_fills_from_sys.mem_io_local,ls_dispatch.ld_dispatch

# Combine all 
ROOFLINE_EVENTS = $(FLOP_EVENTS),$(L1_EVENTS),$(L2_EVENTS),$(L3_EVENTS),$(DRAM_EVENTS)

all: $(TARGET)

$(TARGET): matmul.c
	$(CC) $(CFLAGS) -o $(TARGET) matmul.c

run: $(TARGET)
	taskset -c 0 ./$(TARGET)

perf: $(TARGET)
	taskset -c 0 perf stat -e $(ROOFLINE_EVENTS) ./$(TARGET) 2> perf_stat.txt
# 	@echo "Perf stat saved to perf_stat.txt"

# # Record perf data
# perf-record: $(TARGET)
# 	taskset -c 0 perf record -e $(ROOFLINE_EVENTS) ./$(TARGET)

# # Generate text report from perf.data
# perf-report: perf-record
# 	perf report --stdio > matmul_ijk.txt
# 	@echo "Perf report saved to perf_report.txt"

clean:
	rm -f $(TARGET) perf.data perf_report.txt
