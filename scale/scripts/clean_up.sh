#!/bin/bash
# Get the full path of the directory containing the script
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PARENT_DIR=$(dirname "$SCRIPT_DIR")
DEBUG_LEVEL=${1:-info}  # Default to info if not provided
echo "Cleanup results for the last run ..."

# Function to print debug messages
debug() {
  if [ "$DEBUG_LEVEL" == "debug" ]; then
    echo "$@"
  fi
}

OUTPUT_DIR_LST=(
  "${PARENT_DIR}/outputs/rgn"
  "${PARENT_DIR}/outputs/obj-none"
  "${PARENT_DIR}/outputs/obj-opt"
  "${PARENT_DIR}/outputs/obj-full"
)

DATA_LST=(
    "${PARENT_DIR}/data/rgn.csv"
    "${PARENT_DIR}/data/obj-none.csv"
    "${PARENT_DIR}/data/obj-opt.csv"
    "${PARENT_DIR}/data/obj-full.csv"
)

paper_res="${PARENT_DIR}/paper_results"

for outdir in "${OUTPUT_DIR_LST[@]}"; do
    debug "rm -rf $outdir"
    rm -rf $outdir
done

for data in "${DATA_LST[@]}"; do
    debug "rm -f $data"
    rm -f $data
done

debug "Remove paper results on $paper_res"
find "$paper_res" -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} +