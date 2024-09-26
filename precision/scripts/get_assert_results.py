import json, os

PROJT_ROOT_DIR = os.path.abspath(os.pardir)
SRC_DIR = f'{PROJT_ROOT_DIR}/benchmarks'
DATA_DIR = f'{PROJT_ROOT_DIR}/data'
MOPSA_OUTPUT_DIR = f'{PROJT_ROOT_DIR}/outputs/mopsa'
OBJ_OUTPUT_DIR = f'{PROJT_ROOT_DIR}/outputs/obj'
RGN_OUTPUT_DIR = f'{PROJT_ROOT_DIR}/outputs/rgn'
CRABIR_FILE = 'code.crabir'
MOPSA_JSON_FILE = 'log.json'
PROCESS_RGN = False
PROCESS_OBJ = False
PROCESS_MOPSA = False
# parent directory of current directory

def parse_c_code(c_code_file):
    try:
        with open(c_code_file) as f:
            data = f.readlines()
    except FileNotFoundError:
        print(f"Error: {c_code_file} not found.")
        data = []
    return data

def parse_mopsa_json(json_file):
    try:
        with open(json_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def parse_crabir(crabir_file):
    try:
        with open(crabir_file) as f:
            data = f.readlines()
    except FileNotFoundError:
        data = []
    return data

def process_manual_assertions(c_code_lines, file_name):
    assert_lines = {}
    # Get Line and file name
    for index, line in enumerate(c_code_lines, 1):
        assert_line = {
            'line': index,
            'file': file_name,
            'type': None,
        }
        if line.strip().startswith('assert'):
            assert_line['type'] = 'assert'
        elif line.strip().startswith('ASSERT_IS_DEREF'):
            assert_line['type'] = 'deref'
        else:
            continue
        assert_lines[assert_line['line']] = assert_line
    return assert_lines

def process_crabir_assert_comment(cassert_lines, crabir_lines):
    assert_lines = {}
    for line in crabir_lines:
        assert_line = {
            'line': None,
            'file': None,
            'type': None,
            'result': None,
        }
        if 'loc(file=' in line and 'Result:' in line:
            # loc(file=benchmarks/byte_buf.c line=63 col=3) id=1 Result:  FAIL -- num of warnings=1
            stripped = line.split()
            for cell in stripped:
                if 'line=' in cell:
                    assert_line['line'] = int(cell.split('=')[1])
                elif 'FAIL' in cell:
                    assert_line['result'] = 'WARNING'
                elif 'OK' in cell:
                    assert_line['result'] = 'SAFE'
            assert_line['file'] = cassert_lines[assert_line['line']]['file']
            assert_line['type'] = cassert_lines[assert_line['line']]['type']
        else:
            continue
        assert_lines[assert_line['line']] = assert_line

    for line, info in cassert_lines.items():
        if line not in assert_lines:
            assert_line = {
                'line': info['line'],
                'file': info['file'],
                'type': info['type'],
                'result': 'SAFE',
            }
            assert_lines[line] = assert_line
    return assert_lines

def process_mopsa_assert_json(cassert_lines, mopsa_json):
    assert_lines = {}
    if not mopsa_json:
        return assert_lines
    checks = mopsa_json['checks']
    for check in checks:
        line = None
        if check['title'] != 'Invalid memory access' and check['title'] != 'Assertion failure' and check['title'] != 'Stub condition':
            continue
        if check['title'] == 'Stub condition' and check['callstack'][0]['function'] != '_mopsa_assert_valid_bytes':
            continue

        if check['range']['start']['line'] not in cassert_lines:
            if check['callstack'][0]['range']['start']['line'] not in cassert_lines:
                continue
            line = check['callstack'][0]['range']['start']['line']
        else:
            line = check['range']['start']['line']
        assert_line = {
            'line': None,
            'file': None,
            'type': None,
            'result': None,
        }
        assert_line['line'] = line
        assert_line['file'] = cassert_lines[assert_line['line']]['file']
        assert_line['type'] = cassert_lines[assert_line['line']]['type']
        assert_line['result'] = check['kind'].upper()
        assert_lines[assert_line['line']] = assert_line

    for line, info in cassert_lines.items():
        if line not in assert_lines:
            assert_line = {
                'line': info['line'],
                'file': info['file'],
                'type': info['type'],
                'result': 'SAFE',
            }
            assert_lines[line] = assert_line
    return assert_lines


def process_each_benchmark(benchmark):
    c_code_lines = parse_c_code(benchmark['c_code'])
    cassert_lines = process_manual_assertions(c_code_lines, benchmark['name'])
    obj_crabir_lines = parse_crabir(benchmark['obj']) if PROCESS_OBJ else []
    obj_crabir_assert_lines = process_crabir_assert_comment(cassert_lines, obj_crabir_lines)
    obj_crabir_assert_lines = dict(sorted(obj_crabir_assert_lines.items()))
    rgn_crabir_lines = parse_crabir(benchmark['rgn']) if PROCESS_RGN else []
    rgn_crabir_assert_lines = process_crabir_assert_comment(cassert_lines, rgn_crabir_lines)
    rgn_crabir_assert_lines = dict(sorted(rgn_crabir_assert_lines.items()))
    mopsa_json = parse_mopsa_json(benchmark['mopsa']) if PROCESS_MOPSA else {}
    mopsa_assert_lines = process_mopsa_assert_json(cassert_lines, mopsa_json)
    mopsa_assert_lines = dict(sorted(mopsa_assert_lines.items()))
    return obj_crabir_assert_lines, rgn_crabir_assert_lines, mopsa_assert_lines


def process_all_benchmarks():
    # Get all benchmarks
    benchmarks = []
    for root, dirs, files in os.walk(SRC_DIR):
        for c_file in files:
            benchmark = {}
            if c_file.endswith('.c'):
                benchmark['name'] = c_file.replace('.c', '')
                benchmark['c_code'] = os.path.join(root, c_file)
                benchmark['obj'] = os.path.join(OBJ_OUTPUT_DIR, benchmark['name'], CRABIR_FILE)
                benchmark['rgn'] = os.path.join(RGN_OUTPUT_DIR, benchmark['name'], CRABIR_FILE)
                benchmark['mopsa'] = os.path.join(MOPSA_OUTPUT_DIR, benchmark['name'], MOPSA_JSON_FILE)
                benchmarks.append(benchmark)

    o_res = {}
    r_res = {}
    m_res = {}

    for benchmark in benchmarks:
        o, r, m = process_each_benchmark(benchmark)
        o_res[benchmark['name']] = o
        r_res[benchmark['name']] = r
        m_res[benchmark['name']] = m

    o_res = dict(sorted(o_res.items()))
    r_res = dict(sorted(r_res.items()))
    m_res = dict(sorted(m_res.items()))
    return o_res, r_res, m_res

def arg_parser():
    import argparse
    parser = argparse.ArgumentParser(description='Get assertions from benchmarks')
    parser.add_argument('--rgn', action='store_true', help='Process summarization domain output')
    parser.add_argument('--obj', action='store_true', help='Process mrud domain output')
    parser.add_argument('--mopsa', action='store_true', help='Process mopsa recency domain output')
    return parser.parse_args()


def dump_csv(filename, data, is_json=False):
    try:
        with open(f'{filename}', 'w') as f:
            f.write('name,line,type,result\n')
            for benchmark, asserts in data.items():
                for _, assert_line in asserts.items():
                    f.write(f'{benchmark},{assert_line["line"]},{assert_line["type"]},{assert_line["result"]}\n')
            print(f'Please find the csv file on: {filename}')
    except:
        print(f'Cannot write data into csv {filename}')

def get_assert_results():
    o, r, m = process_all_benchmarks()
    if PROCESS_OBJ:
        o_csv_path = os.path.join(DATA_DIR, 'obj.csv')
        dump_csv(o_csv_path, o)
    if PROCESS_RGN:
        r_csv_path = os.path.join(DATA_DIR, 'rgn.csv')
        dump_csv(r_csv_path, r)
    if PROCESS_MOPSA:
        m_csv_path = os.path.join(DATA_DIR, 'mopsa.csv')
        dump_csv(m_csv_path, m, is_json=True)

if __name__ == '__main__':
    args = arg_parser()
    if args.rgn:
        PROCESS_RGN = True
    if args.obj:
        PROCESS_OBJ = True
    if args.mopsa:
        PROCESS_MOPSA = True
    get_assert_results()