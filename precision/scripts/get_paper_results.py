import pandas as pd
import os
import argparse

DATA_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'data')
RESULTS_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'paper_results')
# do not limit number of rows displayed
pd.set_option('display.max_rows', None)
# Set display options to show all columns
pd.set_option('display.max_columns', None)
# Set a wider max width for columns
pd.set_option('display.width', 1000)
# Left align column headers
pd.set_option('display.colheader_justify', 'center')
# Limit the decimal places to 2 for a cleaner display
pd.set_option('display.float_format', '{:.2f}'.format)
EDGE = 100
WIDTH = 10
SHOW_DETAILS = False
paper_stats = {}

def print_table(data, num):
    # Define the headers
    headers = ['name', '#assert', 'D_o', 'D_s', 'D_r']
    sub_headers = ['', 'safe', 'warning', 'safe', 'warning', 'safe', 'warning']
    # Display the assertion statistics
    print("\n\nAssertion Statistics:")
    print(f"\n\n{'Number of benchmarks:':<{WIDTH}}{num:>{WIDTH}}\n")
    # Print headers
    header_format = "{:^15} {:^8} {:^14} {:^14} {:^14}"
    subheader_format = "{:<24} {:^6} {:^7} {:^6} {:^7} {:^6} {:^7}"
    print(header_format.format(*headers))
    print(' ' * 26 + '-' * 13 + ' ' * 2 + '-' * 13 + ' ' * 2 + '-' * 13)
    print(subheader_format.format(*sub_headers))
    # Print a separator line
    print("-" * 70)
    # Print the rows
    row_format = "{:<16} {:^8} {:^6} {:^7} {:^6} {:^7} {:^6} {:^7}"
    for row in data:
        print(row_format.format(*row))
    print("-" * 70)


def compute_assertion_statistics(df):
    # Initialize the assertion statistics
    statistics = {}

    # Compute the assertion statistics
    for index, row in df.iterrows():
        if row['name'] not in statistics:
            statistics[row['name']] = { '#': 0, 'D_o': {'Proven': 0, 'Difficult': 0} , 'D_s': {'Proven': 0, 'Difficult': 0}, 'D_r': {'Proven': 0, 'Difficult': 0} }
        for domain in ['D_o', 'D_s', 'D_r']:
            if domain not in row:
                continue
            if row[domain] == 'SAFE':
                statistics[row['name']][domain]['Proven'] += 1
            elif row[domain] == 'WARNING':
                statistics[row['name']][domain]['Difficult'] += 1
            else:
                raise ValueError(f"Unexpected value for {domain} in {row['name']}")
        statistics[row['name']]['#'] = statistics[row['name']]['D_o']['Proven'] + statistics[row['name']]['D_o']['Difficult']

    plain_data = []
    for name, assertion_statistics in statistics.items():
        benchmark_data = [name, assertion_statistics['#']]
        for domain in ['D_o', 'D_s', 'D_r']:
            benchmark_data.append(assertion_statistics[domain]['Proven'])
            benchmark_data.append(assertion_statistics[domain]['Difficult'])
        plain_data.append(benchmark_data)
    print_table(plain_data, len(statistics.keys()))


def rename(df, pf):
    # now drop safe,error,warning columns
    df = df.rename(columns = {'result': pf})
    return df

def print_centered_title(title, single="*", width=34):
    """
    Prints a centered title within asterisks of the given width.

    :param title: The title to be centered and printed.
    :param width: The total width of the line (default is 34).
    """
    # Calculate the padding needed to center the title
    padding = (width - len(title)) // 2

    # Adjust padding for titles with odd lengths
    if len(title) % 2 != 0 and width % 2 == 0:
        title += " "

    # Print the formatted output
    print(single * width)
    print(" " * padding + title + " " * padding)
    print(single * width)

def read_csv(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"{path} not found. Proceeding without it.")
        return pd.DataFrame()

def read_csv_files():
    obj = read_csv(os.path.join(DATA_FOLDER, 'obj.csv'))
    rgn = read_csv(os.path.join(DATA_FOLDER, 'rgn.csv'))
    mopsa = read_csv(os.path.join(DATA_FOLDER, 'mopsa.csv'))

    # clam_bench_loc = pd.read_csv(os.path.join(DATA_FOLDER, 'loc.csv'))

    # Output the filtered DataFrame
    obj = rename(obj, 'D_o')
    rgn = rename(rgn, 'D_s')
    mopsa = rename(mopsa, 'D_r')

    if SHOW_DETAILS:
        print('')
        print_centered_title("D_o with OPT reduction", "-")
        print('')
        print(obj)

    if SHOW_DETAILS:
        print('')
        print_centered_title("D_s", "-")
        print('')
        print(rgn)

    if SHOW_DETAILS:
        print('')
        print_centered_title("D_r", "-")
        print('')
        print(mopsa)

    res = pd.merge(obj, rgn, on=['name', 'line', 'type'], how='inner')
    res = pd.merge(res, mopsa, on=['name', 'line', 'type'], how='inner')

    # Assertion Statistics
    # Summarize the number of assertions proven or difficult to prove for each domain in each benchmark
    compute_assertion_statistics(res)


def dump_table():
    pass

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--details', action='store_true', default=False, help='Show more details of the results in table format')
    return parser.parse_args()

if __name__ == '__main__':
    print_centered_title("STATISTICS", "=")
    print(f"\nNote that there is no timeout threshold.")
    print(f"The MRU Domain is represented as 'D_o' in the paper.")
    print(f"The Summarization Domain is represented as 'D_s' in the paper.")
    print(f"The Mopsa Recency Domain is represented as 'D_r' in the paper.")
    args = parse_arguments()
    SHOW_DETAILS = args.details
    read_csv_files()
    if not args.details:
        print(f"\nTo show more details, please run the script ({__file__}) with --details option.")
