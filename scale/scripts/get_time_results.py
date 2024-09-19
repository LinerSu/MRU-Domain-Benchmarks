import os
import csv
import argparse
from enum import Enum

result_pattern1 = "************** ANALYSIS RESULTS ****************"
result_pattern2 = "----------------------------------------------------------------------"
OUT_FOLDER = "data"

# Dictionary to store the parsed numbers
parsed_numbers = {
    "safe": 0,
    "error": 0,
    "warning": 0
}

class Status(Enum):
    DEFAULT = 0
    CLAM_ERROR = 1
    TIMEOUT = 2
    SUCCESS = 3

def read_timimg_results(output_dir, result_dir, result_file, no_check):
    pairs = []
    for dirpath, dirnames, filenames in os.walk(result_dir):
        for filename in filenames:
            if filename == "log.txt":
                log_file = os.path.join(dirpath, filename)
                result_status = Status.DEFAULT
                check_dict = {}
                shown_time_stats = False
                reach_end_stats = False
                with open(log_file, "r") as f:
                    for line in f:
                        if result_pattern1 in line or result_pattern2 in line:
                            reach_end_stats = True
                            if result_status == Status.DEFAULT:
                                result_status = Status.SUCCESS
                        if "** Killed" in line or "CRAB ERROR:" in line:
                            result_status = Status.CLAM_ERROR
                        if "** OS Error:" in line:
                            result_status = Status.TIMEOUT
                        if "bug" in line:
                            result_status = Status.CLAM_ERROR
                        if "BRUNCH_STAT" in line and reach_end_stats and not shown_time_stats:
                            parts = line.strip().split()
                            name = parts[1]
                            raw_name = dirpath.strip().split('/')
                            filename = raw_name[-1]
                            bench_suite = raw_name[-2] if len(raw_name) > 1 else ''
                            if bench_suite != "coreutils":
                                bench_suite = 'others'
                            if name == "Clam" and result_status == Status.SUCCESS:
                                number = float(parts[2])
                                pairs.append([filename, bench_suite, number])
                            elif result_status == Status.CLAM_ERROR:
                                pairs.append([filename, bench_suite, "error"])
                            elif result_status == Status.TIMEOUT:
                                pairs.append([filename, bench_suite, "timeout"])
                            elif result_status == Status.DEFAULT:
                                pairs.append([filename, bench_suite, "no result"])
                            shown_time_stats = True
                        if result_status == Status.SUCCESS:
                            if "safe checks" in line:
                                number = int(line.strip().split()[0])
                                check_dict['safe'] = number
                            if "error checks" in line:
                                number = int(line.strip().split()[0])
                                check_dict['error'] = number
                            if "warning checks" in line:
                                number = int(line.strip().split()[0])
                                check_dict['warning'] = number
                if result_status == Status.DEFAULT:
                    continue
                if not no_check and result_status == Status.SUCCESS:
                    pairs[-1].extend([check_dict['safe'], check_dict['error'], check_dict['warning']])
                else:
                    pairs[-1].extend([0,0,0])
    draw_results_table(pairs, output_dir, result_file)


def draw_results_table(pairs, output_dir, result_file):
    csv_name = output_dir + "/"+ result_file + ".csv"
    try:
        with open(csv_name, "w", newline="") as f:
            writer = csv.writer(f)
            col_name = ["name", "suite", "time"]
            col_name.extend(parsed_numbers.keys())
            writer.writerow(col_name)
            for pair in pairs:
                writer.writerow(pair)
            print(f'Please find the csv file on: {os.path.abspath(csv_name)}')
    except:
        print(f'Cannot write data into csv {os.path.abspath(csv_name)}')

def args_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", required=True)
    parser.add_argument('--output-dir', dest='output_dir', action='store', required=True)
    parser.add_argument('--no-check', action='store_true', dest='no_check', default=False, required=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = args_parse()
    outdir = os.path.dirname(os.getcwd())
    outdir = os.path.join(outdir, OUT_FOLDER)
    print(f'Read timing and check results from the folder: {args.output_dir}')
    read_timimg_results(outdir, args.output_dir, args.filename, args.no_check)