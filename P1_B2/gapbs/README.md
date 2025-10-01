# Q 1.1

This provides scripts to reproduce BFS performance counters, generate TEPS graphs, analyze optimization speedups, and regenerate the Roofline model.

---

## 1. Reproduce TEPS counters

```bash
chmod +x ./reproduce_perf_counters.sh
sudo ./reproduce_perf_counters.sh
```


## 2. Reproduce n_vertices vs TEPS graph (theoretical TEPS peak)

```bash
chmod +x ./peak_teps.sh
./peak_teps.sh
```
This will generate:

bfs_performance_graph.png


## 3. Generate optimization speedup graph

```bash
chmod +x ./evaluate_reordering.sh
./evaluate_reordering.sh
```
This will generate:

bfs_runtime_vs_vertices.png

## 4. Regenerate the Roofline plot

```bash
cd vizualization_script
pip install -r requirements.txt
python viz_roofline.py
```
 

