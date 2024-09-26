#!/bin/bash
CLAM_DIR=$1 # /home/agent/tool/clam/
MOPSA_DIR=$2 # /home/agent/tool/mopsa/
# by default, run: ./run_precision_experiments.sh $CLAM_DIR $OPAM_SWITCH_PREFIX
# Cleanup all previous runs
./clean_up.sh

mkdir -p /tmp/results/precision

# Run the experiments
# 1. Run experiment for the summarization domain (in crab, we called region domain)
./run_experiment.sh $CLAM_DIR rgn

# 2. Run experiment for the MRU domain (with heuristic reduction)
./run_experiment.sh $CLAM_DIR obj

# 3. Run experiment for the Mopsa Recency domain
./run_experiment.sh $MOPSA_DIR mopsa

# Generate paper results in a log file
echo "\n\n================================================"
echo "                 STATISTICS                 "
echo "================================================\n\n"
python3 get_paper_results.py &> ../paper_results/results.txt

echo "Please find paper results in precision/paper_results directory"