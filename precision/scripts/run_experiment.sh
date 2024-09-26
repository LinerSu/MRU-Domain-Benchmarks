#!/bin/bash
# arguments: $1: TOOL_DIR, $2: DOM, $3: DEBUG_LEVEL
TOOL_DIR=$1 # /home/yusen/seawork/clam/
DOM=$2
# Set the clam directory
# Set the debug level (info, debug)
DEBUG_LEVEL=${3:-info}  # Default to info if not provided

# Function to print debug messages
debug() {
  if [ "$DEBUG_LEVEL" == "debug" ]; then
    echo "$@"
  fi
}

mkdir -p /tmp/results/precision

# Function to print a centered title within asterisks of the given width
print_centered_title() {
    local title="$1"
    local single="${2:-*}"  # Default to "*" if not provided
    local width="${3:-34}"  # Default to 34 if not provided

    # Calculate the padding needed to center the title
    local title_length=${#title}
    local padding=$(( (width - title_length) / 2 ))

    # Adjust padding for titles with odd lengths
    if [ $((title_length % 2)) -ne 0 ] && [ $((width % 2)) -eq 0 ]; then
        title="$title "
    fi

    # Print the formatted output
    printf "\n\n%${width}s\n" | tr " " "$single"
    printf "%*s%s%*s\n" $padding "" "$title" $padding ""
    printf "%${width}s\n\n" | tr " " "$single"
}

# Get the full path of the directory containing the script
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PARENT_DIR=$(dirname "$SCRIPT_DIR")
CLAM_PY="run/bin/clam-yaml.py"
MOPSA_BIN="bin/mopsa-c"

BENCH_DIR_NAME="benchmarks"
BENCH_DIR="${PARENT_DIR}/${BENCH_DIR_NAME}"
STATS_FILE="stats.txt"
YAML_FILE="${PARENT_DIR}/configs/clam.yaml"
JSON_FILE="${PARENT_DIR}/configs/mopsa_rel.json"

list="$(find $BENCH_DIR -type f -name '*.c')"

# Check the value of DOM and echo the appropriate message or abort
if [ "$DOM" == "rgn" ]; then
  print_centered_title "Using summarization domain" "=" 34
  OUTPUT_DIR="${PARENT_DIR}/outputs/${DOM}"
  FILE_NAME=${DOM}
  CLAM_CMD="${TOOL_DIR}/build_rgn/${CLAM_PY}"
  LOG_FILE="log.txt"
elif [ "$DOM" == "obj" ]; then
  print_centered_title "Using the MRU domain with heuristics reduction" "=" 60
  OUTPUT_DIR="${PARENT_DIR}/outputs/${DOM}"
  FILE_NAME=${DOM}
  CLAM_CMD="${TOOL_DIR}/build/${CLAM_PY}"
  LOG_FILE="log.txt"
elif [ "$DOM" == "mopsa" ]; then
    print_centered_title "Using the Recency domain with MOPSA" "=" 40
    OUTPUT_DIR="${PARENT_DIR}/outputs/${DOM}"
    FILE_NAME=${DOM}
    EXTRA_CMD="-numeric octagon -widening-delay=2 -loop-decr-it -stub-ignore-case malloc.failure -debug print -format json"
    MOPSA_CMD="${TOOL_DIR}/${MOPSA_BIN} ${EXTRA_CMD}"
    LOG_FILE="log.json"
else
  echo "Invalid domain. Aborting."
  exit 1
fi

# WARN: Remove all files
debug "rm -rf ${OUTPUT_DIR}/*"
# rm -rf ${OUTPUT_DIR}/*

# Run the experiments
if [ "$DOM" == "mopsa" ]; then
    for cfile in $list;
    do
    file=${cfile%.c}
    name=${file##*/}
    subdir=${OUTPUT_DIR}/${name}
    mopsajson="${name}.json"
    mkdir -p ${subdir}
    debug "<-- start with $name.c"
    debug "${MOPSA_CMD} -config ${JSON_FILE} $cfile > ${subdir}/${LOG_FILE} 2>&1"
    ${MOPSA_CMD} -config ${JSON_FILE} $cfile > ${subdir}/${LOG_FILE} 2>&1
    ret_sig=$?
    # exit 0
    if [ $ret_sig -ne 0 ]; then
        debug "Failed on $bc --> No!"
    else
        debug "Passed -->"
    fi
    done
else
    for cfile in $list;
    do
    file=${cfile%.c}
    name=${file##*/}
    subdir=${OUTPUT_DIR}/${name}
    crabir="code.crabir"
    mkdir -p ${subdir}
    debug "<-- start with $name.c"
    # ( "--bounds"
    debug "${CLAM_CMD} -y ${YAML_FILE} $cfile -ocrab=${subdir}/${crabir} > ${subdir}/${LOG_FILE} 2>&1"
    ${CLAM_CMD} -y ${YAML_FILE} $cfile -ocrab=${subdir}/${crabir} > ${subdir}/${LOG_FILE} 2>&1
    ret_sig=$?
    # exit 0
    if [ $ret_sig -ne 0 ]; then
        debug "Failed on $bc --> No!"
    else
        debug "Passed -->"
    fi
    # ) &
    done
fi


printf "\n\nGenerating results ... \n\n"
python3 get_assert_results.py --"$DOM"