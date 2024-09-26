#!/bin/bash
TOOL_DIR=$1 # /home/agent/tool/clam/
# by default, run: ./run_scale_experiments.sh $CLAM_DIR
# Cleanup all previous runs
./clean_up.sh

mkdir -p /tmp/results/scale

# Run the experiments

# 1. Run experiment for the summarization domain (in crab, we called region domain)
./run_experiment.sh $TOOL_DIR rgn

# 2. Run experiment for the MRU domain (with no reduction)
./run_experiment.sh $TOOL_DIR obj none

# 3. Run experiment for the MRU domain (with heuristic reduction)
./run_experiment.sh $TOOL_DIR obj opt

# 4. Run experiment for the MRU domain (with full reduction)
./run_experiment.sh $TOOL_DIR obj full

# Generate scatter plot (as figure in the paper) and paper results in a log file

echo "\n\n================================================"
echo "                 STATISTICS                 "
echo "================================================\n\n"
python3 get_paper_results.py &> ../paper_results/results.txt

echo "Please find scatter plot and paper results in scale/paper_results directory"