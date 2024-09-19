import sys
import re
import os
import csv
import glob
import math
import subprocess
import argparse

HARNESS_PATH = 'bitcode_llvm14'

def get_regex():
    name_1 = r"^define\s+"
    regexp1 = re.compile(name_1)
    name_2 = r'^attributes\s+'
    regexp2 = re.compile(name_2)
    name_3 = r'^\d+:\s*;\s*preds\s*=\s*%\d+'
    regexp3 = re.compile(name_3)
    return regexp1, regexp2, regexp3

def compute_funcs_loc(file):
    """
    This function compute line of code by approximation since function
    may not be call directly, and all syscalls will be ignored
    """
    start_regex, end_regex, bb_name_regex = get_regex()
    curr_loc = 0
    start = False
    count = 0
    for line in file:
        if start_regex.search(line):
            start = True
        if line.strip() == '}':
            start = False
        if end_regex.search(line):
            break
        if start and line != "\n" and not bb_name_regex.search(line):
            curr_loc += 1
    return curr_loc


def read_output_from_file(file_name, bench_name):
    try:
        file = open(file_name, 'r')
    except BaseException:
        sys.exit("human readable bitcode (.ll) file does not exits. Exit!")
    if args.debug:
        print(f'start compute loc for bit code <{bench_name}>')
    res_data = ['', '']
    # 1. Add bit code name
    res_data[0] = bench_name
    loc = [0]
    # 2. Add loc for each bit code
    res_data[1] = compute_funcs_loc(file)
    if args.debug:
        print(f'har. {bench_name} with loc comp. {res_data[1]}...')
    file.close()
    return res_data


def run_llvmdis_for_job(res_data, file_path, file_name):
    """
     # This function converts bitcode file into human readable files
     # The command line is 'llvm-dis-10 <file_name>.bc'
     # Then it will call function to compute loc based on .ll file
     # @param res_data store all the infor we collected.
     # @return nothing, use call by ref.
    """
    print("Start making LOC results ...")
    if not os.path.exists(file_path[:-2] + "ll"):
        command_lst = [f'llvm-dis-14 {file_path}']
        cmd_llvmdis = ""
        for strcmd in command_lst:
            cmd_llvmdis += strcmd + " ; "
        print(cmd_llvmdis)
        process = subprocess.Popen(
            '/bin/bash',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        _ = process.communicate(cmd_llvmdis.encode())
    file_path = file_path[:-2] + "ll"
    # compute the loc
    res_data.append(read_output_from_file(file_path, file_name))
    return res_data


def write_data_into_csv(file_name, res_data):
    with open(file_name, 'w+', newline='') as csvfile:
        # create the csv writer object
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Name", "LOC"])
        for row in res_data:
            # data = ', '.join(row)
            csvwriter.writerow(row)

def compute_loc(base_dir):
    res_data = []
    # Walk through the directory structure
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            # Check if the file is a text file (you may need to adjust this condition)
            if file.endswith('.bc'):
                file_path = os.path.join(root, file)
                # Get the LOC
                rest_data = run_llvmdis_for_job(res_data, file_path, file[:-3])
                # Determine the subfolder or mark as blank if directly under base_dir
                subfolder = os.path.relpath(root, base_dir)
                if subfolder == '.':
                    subfolder = ''  # Mark as blank if the file is directly under base_dir
                # Store the info
                res_data[-1].append(subfolder)
                # Remove ll file
                # file_path = file_path[:-2] + "ll"
                # if os.path.exists(file_path):
                #     os.remove(file_path)
    return res_data

def write_data_into_csv(file_name, res_data):
    with open(file_name, 'w+', newline='') as csvfile:
        # create the csv writer object
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["name", "loc", "suite"])
        for row in res_data:
            # data = ', '.join(row)
            csvwriter.writerow(row)


def main():
    res_data = compute_loc(HARNESS_PATH)
    write_data_into_csv("{file}".format(file='loc.csv'), res_data)


if __name__ == "__main__":
    # Args for this script
    parser = argparse.ArgumentParser(
        description='Present debug flag if using debug mode.')
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()
    main()
