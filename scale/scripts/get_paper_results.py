import pandas as pd
import numpy as np
import copy
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import matplotlib.pyplot as plt
from termcolor import colored
import scipy
import os
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
TIMEOUT_THRESHOLD = 5000
EDGE = 100
WIDTH = 10
DATA_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'data')
RESULTS_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'paper_results')
paper_stats = {}

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

def compute_speedup_percentage(name, redtype, old, new):
    if old == 0:
        if new - old > 1.0:
            raise ValueError(f"Region: {old}, {redtype}: {new}, name: {name}")
        return 0.0
    return ((old - new) / old) * 100

def compute_real_slower_time_on_average(name, redtype, slower, faster):
    return slower - faster

def show_graph(fig, time_plot, lst, b, title):
    # # Perform KDE on data
    # values = np.vstack([time_plot[a], time_plot[b]])
    # kernel = gaussian_kde(values)

    # # Evaluate density on the data points
    # time_plot['density'] = kernel(values)
    # print(time_plot['density'])
    # time_plot['size'] = 1 / (time_plot['density'] * 3000)
    # print(time_plot['size'])
    # Assuming 'figsize' is known
    df_melted = time_plot.melt(id_vars=b, value_vars=lst,
                        var_name='Reduction Config', value_name='obj_time')
    shape_lst = ['o', 'x', 's']
    fig_width, fig_height = plt.gcf().get_size_inches()
    # You might base size on some function of plot dimensions
    point_size = (fig_width * fig_height) * 0.7  # Example formula
    # plt.title(title, fontsize=24)
    plt.rc('legend', fontsize=20, title_fontsize=26)
    x_padding = (TIMEOUT_THRESHOLD - 0) * 0.009  # % padding
    y_padding = (TIMEOUT_THRESHOLD - 0) * 0.009  # % padding
    plt.xlim(-x_padding, TIMEOUT_THRESHOLD + x_padding)
    plt.ylim(-y_padding, TIMEOUT_THRESHOLD + y_padding)
    plt.xlabel('MRUD (seconds)', fontsize=36)
    plt.ylabel('Summarization (seconds)', fontsize=36)
    x = np.linspace(0, TIMEOUT_THRESHOLD, TIMEOUT_THRESHOLD, 2)
    plt.plot(x, x)
    pp_g = sns.scatterplot(x='obj_time', y=b, data=df_melted, hue='Reduction Config', alpha=0.8, style='Reduction Config', s=point_size)
    sns.despine()
    pp_g.set_xticks([0, 1000, 2000, 3000, 4000, 5000])
    pp_g.set_yticks([0, 1000, 2000, 3000, 4000, 5000])
    pp_g.spines['left'].set_position('zero')
    line_width = pp_g.spines['left'].get_linewidth()
    pp_g.spines['left'].set_bounds(0, TIMEOUT_THRESHOLD)
    pp_g.spines['bottom'].set_position('zero')
    pp_g.spines['bottom'].set_bounds(0, TIMEOUT_THRESHOLD)
    pp_g.set_xticklabels(pp_g.get_xticks(), size=28)
    pp_g.set_yticklabels(pp_g.get_yticks(), size=28)
    sns.move_legend(pp_g, "lower right", bbox_to_anchor=(TIMEOUT_THRESHOLD/(TIMEOUT_THRESHOLD + x_padding), y_padding/(TIMEOUT_THRESHOLD + y_padding)))
    # Manually add gridlines up to x_max
    for x_tick, y_tick in zip(pp_g.get_xticks(), pp_g.get_yticks()):
        if x_tick != 0 and x_tick < TIMEOUT_THRESHOLD:
            pp_g.vlines(x_tick, ymin=0, ymax=TIMEOUT_THRESHOLD, linewidth=line_width, color='gray', linestyle='--', alpha=0.7)  # Lighter gridline
        if y_tick != 0 and y_tick < TIMEOUT_THRESHOLD:
            pp_g.hlines(y_tick, xmin=0, xmax=TIMEOUT_THRESHOLD, linewidth=line_width, color='gray', linestyle='--', alpha=0.7)  # Lighter gridline
    # pp_g.grid(True)
    pp_g.vlines(x=TIMEOUT_THRESHOLD, ymin=0, ymax=TIMEOUT_THRESHOLD, linewidth=line_width, color='black', linestyle='-', alpha=0.7)
    pp_g.hlines(y=TIMEOUT_THRESHOLD, xmin=0, xmax=TIMEOUT_THRESHOLD, linewidth=line_width, color='black', linestyle='-', alpha=0.7)
    plt.tight_layout()
    # plt.show()

def show_loc_bar_graph(df, a, b, c):
    fig, ax = plt.subplots(figsize=(20, 12))
    scatter = sns.scatterplot(
        data=df, 
        x=a, 
        y=b, 
        # size=c, 
        hue=c, 
        palette='Blues',  # Change the palette as needed
        # sizes=(20, 200),  # Adjust the size range as needed
        legend=False,
        ax=ax             # Use the specified axes
    )
    plt.xlim(0, TIMEOUT_THRESHOLD+ 30)
    plt.ylim(0, TIMEOUT_THRESHOLD+ 30)
    tmp = df[(df[a] < TIMEOUT_THRESHOLD) & (df[b] < TIMEOUT_THRESHOLD)]


    # Calculate the regression line
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(tmp[a], tmp[b])
    line = slope * np.array(tmp[a])
    plt.plot(tmp[a], line, color='blue', label='Trend Line')

    # Create a color bar with the same figure
    norm = plt.Normalize(tmp[c].min(), tmp[c].max())
    sm = plt.cm.ScalarMappable(cmap="Blues", norm=norm)
    sm.set_array([])

    # Add the color bar to the figure
    cbar = fig.colorbar(sm, ax=ax)

    # Set plot title and labels
    # ax.set_title('Scatter Plot Comparing Two Columns Based on LOC')
    ax.set_xlabel(a)
    ax.set_ylabel(b)

    # Show plot
    plt.show()


def compute_count(df):
    df = df.copy()
    category_counts = df['time'].value_counts()

    # Print counts
    print(f"{'- Number of error occurrences:':<{WIDTH}} {category_counts.get('error', 0)}")
    error_lst = df[df['time'] == 'error']['name'].to_list()
    print(f"    {'Error list:':<{WIDTH}} {error_lst}")
    print(f"{'- Number of no result occurrences:':<{WIDTH}} {category_counts.get('no result', 0)}")
    nores_lst = df[df['time'] == 'no result']['name'].to_list()
    print(f"    {'No Result list:':<{WIDTH}} {nores_lst}")
    print(f"{'- Number of timeout occurrences:':<{WIDTH}} {category_counts.get('timeout', 0)}")
    to_lst = df[df['time'] == 'timeout']['name'].to_list()
    print(f"    {'Timeout list:':<{WIDTH}} {to_lst}")
    # Filter DataFrame for rows where 'time' is 'error', 'no result'
    df = df[~df['time'].isin(['error', 'no result'])]
    # Set maximum Time on DataFrame for rows where 'timeout'
    df.loc[df['time'] == 'timeout', 'time'] = TIMEOUT_THRESHOLD
    df['time'] = df['time'].astype(float)
    df['time'] = df['time'].round(0)
    return df

def rename_and_drop(df, pf):
    # now drop safe,error,warning columns
    df = df.rename(columns = {'time': pf})
    df = df.drop(['safe', 'error', 'warning'], axis=1)
    df = df.drop(['suite'], axis=1)
    return df


def read_csv_files():
    clam_bench_obj_no = pd.read_csv(os.path.join(DATA_FOLDER, 'obj-none.csv'))
    clam_bench_obj_opt = pd.read_csv(os.path.join(DATA_FOLDER, 'obj-opt.csv'))
    clam_bench_obj_full = pd.read_csv(os.path.join(DATA_FOLDER, 'obj-full.csv'))
    clam_bench_rgn = pd.read_csv(os.path.join(DATA_FOLDER, 'rgn.csv'))
    # clam_bench_loc = pd.read_csv(os.path.join(DATA_FOLDER, 'loc.csv'))
    black_list = ['lua', 'luac', 'sqlite3', 'tmux', 'php', 'php-cgi', 'phpdbg']
    clam_bench_obj_no = clam_bench_obj_no[~clam_bench_obj_no['name'].isin(black_list)]
    clam_bench_obj_opt = clam_bench_obj_opt[~clam_bench_obj_opt['name'].isin(black_list)]
    clam_bench_obj_full = clam_bench_obj_full[~clam_bench_obj_full['name'].isin(black_list)]
    clam_bench_rgn = clam_bench_rgn[~clam_bench_rgn['name'].isin(black_list)]
    paper_stats['total'] = len(clam_bench_obj_no)
    print(f"\n\n{'Number of benchmarks:':<{WIDTH}}{len(clam_bench_obj_no):>{WIDTH}}")

    # Output the filtered DataFrame
    print("\n\nFor D_o with no reduction:\n")
    filtered_obj_no = rename_and_drop(compute_count(clam_bench_obj_no), 'NONE')

    print("\n\nFor D_o with OPT reduction:\n")
    filtered_obj_opt = rename_and_drop(compute_count(clam_bench_obj_opt), 'OPT')

    print("\n\nFor D_o with FULL reduction")
    filtered_obj_full = rename_and_drop(compute_count(clam_bench_obj_full), "FULL")

    print("\n\nFor D_s")
    filtered_rgn = rename_and_drop(compute_count(clam_bench_rgn), "Region")
    
    obj = pd.merge(filtered_obj_no, filtered_obj_opt, on='name', how='inner')
    obj = pd.merge(obj, filtered_obj_full, on='name', how='inner')
    res = pd.merge(obj, filtered_rgn, on='name', how='inner')
    filtered_rgn_tm = res[(res['Region'] == TIMEOUT_THRESHOLD) & (res['NONE'] < TIMEOUT_THRESHOLD)]

    # Generate a scatter plot
    fig = plt.figure(figsize=(15, 12))
    show_graph(fig, res, ['NONE', 'OPT', 'FULL'], 'Region', f'Total Running Time Comparison')
    pic_path = os.path.join(RESULTS_FOLDER, 'SP_clam.png')
    plt.savefig(pic_path)
    print(f"\n\n{'Scatter plot saved at:':<{WIDTH}}{pic_path:>{WIDTH}}")

    # Timeout Statistics
    # Number of cases that both timeouts
    tm = len(res[(res['FULL'] == TIMEOUT_THRESHOLD) & (res['Region'] == TIMEOUT_THRESHOLD)])
    print(f"\n\n{'Number of cases that both domains timeout:':<{WIDTH}}{tm:>{WIDTH}}")

    # Number of cases that object domain terminates but rgn does not
    rgn_tm = len(res[(res['Region'] == TIMEOUT_THRESHOLD) & (res['NONE'] < TIMEOUT_THRESHOLD)])
    print(f"{'Number of cases that D_o terminates but D_s does not:':<{WIDTH}}{rgn_tm:>{WIDTH}}")

    # Excluding timeout cases for both object and region
    res_notm = res[(res['Region'] < TIMEOUT_THRESHOLD) & (res['NONE'] < TIMEOUT_THRESHOLD)]
    res = res_notm
    
    # Timing Comparison
    # show the number of benchmarks right now
    print(f"{'Number of benchmarks for comarisons (excluding timeout cases):':<{WIDTH}}{len(res):>{WIDTH}}")

    # show timing statitics
    stats = res[res.columns.difference(['name'])].describe()
    stats = stats[['Region', 'NONE', 'OPT', 'FULL']].rename(columns={'Region': 'D_s', 'NONE': 'D_o with NONE Reduction', 'OPT': 'D_o with OPT Reduction', 'FULL': 'D_o with FULL Reduction'})
    print(f"\n\nShow detailed timing statistics for each domain:")
    print(stats)

    outperform_percentage = {}

    for column in ['NONE', 'OPT', 'FULL']:
        outperform_percentage[column] = res.apply(lambda row: compute_speedup_percentage(row['name'], column, row['Region'], row[column]), axis=1).mean()

    # Display the results
    print("\n\nThe average percentage comparison of D_o with D_s:")
    for column, percentage in outperform_percentage.items():
        print(f"D_o with {column:<4} Reduction improves D_s {percentage:.2f}% of the time on average.")

    print("\n\nThe reduction time difference between the reduction strategy:")
    reduction_time_diff = {}
    for column in ['NONE', 'OPT']:
        reduction_time_diff[column] = res.apply(lambda row: compute_real_slower_time_on_average(row['name'], column, row['FULL'], row[column]), axis=1).mean()

    for column, diff in reduction_time_diff.items():
        print(f"D_o with FULL is slower than {column:<4} {int(diff)} seconds on average.")

if __name__ == '__main__':
    print_centered_title("STATISTICS", "=")
    print(f"\nNote that the timeout threshold is {TIMEOUT_THRESHOLD} seconds.")
    print(f"The MRU Domain is represented as 'D_o' in the paper.")
    print(f"The Summarization Domain is represented as 'D_s' in the paper.")
    read_csv_files()