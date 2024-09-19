#!/bin/bash
# Cleanup all previous runs
./clean_up.sh

# Run the experiments

# 1. Run experiment for the summarization domain (in crab, we called region domain)
./run_experiments.sh rgn

# 2. Run experiment for the MRU domain (with no reduction)
./run_experiments.sh obj none

# 3. Run experiment for the MRU domain (with heuristic reduction)
./run_experiments.sh obj opt

# 4. Run experiment for the MRU domain (with full reduction)
./run_experiments.sh obj full

# Generate scatter plot (as figure in the paper) and paper results in a log file
divider="================================================"

echo "$divider"
echo "           STATISTICS            "
echo "$divider"
python3 get_paper_results.py &> ../paper_results/log.txt

echo "Please find scatter plot and paper results in scale/paper_results directory"