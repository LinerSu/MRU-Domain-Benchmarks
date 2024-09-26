#!/bin/bash
# arguments: $1: TOOL_DIR, $2: DOM, $3: DEBUG_LEVEL
TOOL_DIR=$1 # /home/agent/clam/
DOM=$2
OBJ_MODE=${3:-none} # Default to none if not provided
# Set the debug level (0: no debug, 1: basic debug, 2: detailed debug)
DEBUG_LEVEL=${4:-info}  # Default to info if not provided

# Function to print debug messages
debug() {
  if [ "$DEBUG_LEVEL" == "debug" ]; then
    echo "$@"
  fi
}

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
    printf "%${width}s\n" | tr " " "$single"
    printf "%*s%s%*s\n" $padding "" "$title" $padding ""
    printf "%${width}s\n" | tr " " "$single"
}

# Get the full path of the directory containing the script
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PARENT_DIR=$(dirname "$SCRIPT_DIR")
# Bunch of variables
CLAM_CMD="./verify.py"
BENCH_DIR_NAME="bitcode_llvm14"
BENCH_DIR="${PARENT_DIR}/${BENCH_DIR_NAME}"
LOG_FILE="log.txt"
STATS_FILE="stats.txt"
timeout="5000s"
black_list="lua luac sqlite3 tmux php php-cgi phpdbg" # bftpd vsftpd thttpd brotli curl
black_list=$(echo $black_list | tr ' ' '\n')
list="$(find $BENCH_DIR -type f -name '*.bc')"
# list="$BENCH_DIR/coreutils/true.bc"

# Check if DOM is provided
if [ -z "$DOM" ]; then
  echo "DOM is required. Aborting."
  exit 1
fi

# Check the value of DOM and echo the appropriate message or abort
if [ "$DOM" == "rgn" ]; then
  print_centered_title "Using summarization domain" "=" 34
  OUTPUT_DIR="${PARENT_DIR}/outputs/${DOM}"
  FILE_NAME=${DOM}
elif [ "$DOM" == "obj" ]; then
  if [ -z "$OBJ_MODE" ]; then
    echo "OBJ_MODE is required for obj domain. Aborting."
    exit 1
  elif [ "$OBJ_MODE" == "none" ]; then
    print_centered_title "Using the MRU domain with no reduction" "=" 60
  elif [ "$OBJ_MODE" == "opt" ]; then
    print_centered_title "Using the MRU domain with heuristics reduction" "=" 60
  elif [ "$OBJ_MODE" == "full" ]; then
    print_centered_title "Using the MRU domain with full reduction" "=" 60
  else
    echo "Invalid OBJ_MODE. Aborting."
    exit 1
  fi
  OUTPUT_DIR="${PARENT_DIR}/outputs/${DOM}-${OBJ_MODE}"
  FILE_NAME=${DOM}-${OBJ_MODE}
else
  echo "Invalid domain. Aborting."
  exit 1
fi

# WARN: Remove all files
rm -rf ${OUTPUT_DIR}/*

# Run the experiments
for bc in $list;
do
  file=${bc%.bc}
  name=${file##*/}
  dir_part=${file%/*}
  last_dir=${dir_part##*/}
  if [[ "${last_dir}" == "coreutils" ]]; then
    debug "<-- start with $BENCH_DIR_NAME/$last_dir/$name.bc"
  else
    debug "<-- start with $BENCH_DIR_NAME/$name.bc"
  fi
  if echo "$black_list" | grep -qx "$name"; then
    debug "skip $bc -->YEAH!!!"
    continue
  fi
  subdir=${OUTPUT_DIR}/${name}
  crabir="${name}.crabir"
  if [[ "${last_dir}" == "coreutils" ]]; then
    subdir=${OUTPUT_DIR}/${last_dir}/${name}
  fi
  mkdir -p ${subdir}
  # ( "--bounds"
  # echo "${timeout} ${CLAM_CMD} "--mem-dom" $DOM $bc -ocrab=${subdir}/${crabir} > ${subdir}/${LOG_FILE} 2>&1"
  timeout ${timeout} ${CLAM_CMD} "--tool-dir" $TOOL_DIR  "--mem-dom" $DOM $bc -ocrab=${subdir}/${crabir} > ${subdir}/${LOG_FILE} 2>&1
  ret_sig=$?
  # exit 0
  if [ $ret_sig -eq 124 ]; then
    debug "Timeout -->"
  elif [ $ret_sig -ne 0 ]; then
    debug "Failed on $bc --> No!"
  else
    debug "Passed -->"
  fi
  # ) &
done

# wait

printf "\n\nGenerating results ... \n\n"
python3 get_time_results.py --output-dir ${OUTPUT_DIR} --filename ${FILE_NAME} --no-check
# list="$(find $OUTPUT_DIR -type f -name '*.crabir')"
# for bc in $list;
# do
#   file=${bc%.crabir}
#   bc=${file##*/}
#   echo "----------------------------------------"
#   echo "$bc"
#   echo "----------------------------------------"
#   bc="${OUTPUT_DIR}/$bc"
#   ./read_results.py ${bc}.crabir >> ${OUTPUT_DIR}/${STATS_FILE} 2>&1
# done