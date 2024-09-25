import json, os

PROJT_ROOT_DIR = os.path.abspath(os.pardir)
SRC_DIR = f'{PROJT_ROOT_DIR}/benchmarks'
MOPSA_OUTPUT_DIR = f'{PROJT_ROOT_DIR}/outputs/mopsa'
OBJ_OUTPUT_DIR = f'{PROJT_ROOT_DIR}/outputs/obj'
RGN_OUTPUT_DIR = f'{PROJT_ROOT_DIR}/outputs/rgn'
CRABIR_FILE = 'code.crabir'
MOPSA_JSON_FILE = 'log.json'
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
            assert_line['type'] = 'assert'
        else:
            continue
        assert_lines[assert_line['line']] = assert_line
    # find if the line in cassert_lines is not in assert_lines
    for line in cassert_lines:
        if line not in assert_lines:
            tmp_assert_line = cassert_lines[line]
            raise ValueError(tmp_assert_line)
            # tmp_assert_line['result'] = 'false'
            # assert_lines[line] = cassert_lines[line]
    return assert_lines

def process_mopsa_assert_json(cassert_lines, mopsa_json):
    checks = mopsa_json['checks']
    pass


def process_each_benchmark(benchmark):
    c_code_lines = parse_c_code(benchmark['c_code'])
    obj_crabir_lines = parse_crabir(benchmark['obj'])
    rgn_crabir_lines = parse_crabir(benchmark['rgn'])
    cassert_lines = process_manual_assertions(c_code_lines, benchmark['name'])
    obj_crabir_assert_lines = process_crabir_assert_comment(cassert_lines, obj_crabir_lines)
    print(obj_crabir_assert_lines)
    exit(0)
    rgn_crabir_assert_lines = process_crabir_assert_comment(cassert_lines, rgn_crabir_lines)
    mopsa_json = parse_mopsa_json(benchmark['mopsa'])
    mopsa_assert_lines = process_mopsa_assert_json(cassert_lines, mopsa_json)
    return cassert_lines, obj_crabir_assert_lines, rgn_crabir_assert_lines, mopsa_assert_lines


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

    for benchmark in benchmarks:
        ret = process_each_benchmark(benchmark)
        print(ret)
    return


if __name__ == '__main__':
    process_all_benchmarks()