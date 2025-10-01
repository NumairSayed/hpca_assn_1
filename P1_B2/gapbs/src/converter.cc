// Copyright (c) 2015, The Regents of the University of California (Regents)
// See LICENSE.txt for license details

#include <iostream>

#include "benchmark.h"
#include "builder.h"
#include "command_line.h"
#include "graph.h"
#include "writer.h"
#include "timer.h"

using namespace std;

int main(int argc, char* argv[]) {
  CLConvert cli(argc, argv, "converter");
  cli.ParseArgs();
  if (cli.out_weighted()) {
    WeightedBuilder bw(cli);
    WGraph wg = bw.MakeGraph();
    // Check if the reorder flag is set
    if (cli.reorder()) {
      cout << "Reordering graph with Reverse Cuthill-McKee..." << endl;
      Timer rcm_timer;
      rcm_timer.Start();
      wg = WeightedBuilder::RelabelByRCM(wg);
      rcm_timer.Stop();
      PrintTime("RCM Relabel Time", rcm_timer.Seconds());
    }
    wg.PrintStats();
    WeightedWriter ww(wg);
    ww.WriteGraph(cli.out_filename(), cli.out_sg());
  } else {
    Builder b(cli);
    Graph g = b.MakeGraph();
    // Check if the reorder flag is set
    if (cli.reorder()) {
      cout << "Reordering graph with Reverse Cuthill-McKee..." << endl;
      Timer rcm_timer;
      rcm_timer.Start();
      g = Builder::RelabelByRCM(g);
      rcm_timer.Stop();
      PrintTime("RCM Relabel Time", rcm_timer.Seconds());
    }
    g.PrintStats();
    Writer w(g);
    w.WriteGraph(cli.out_filename(), cli.out_sg());
  }
  return 0;
}