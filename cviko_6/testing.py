'''Module for testing homework assignment solutions in Introduction to programming in Python'''

from math import trunc
import multiprocessing
from re import L
import sys

if sys.version_info < (3, 6):
    message = 'This module is implemented for Python version 3.6 or higher. \nYour are currently running: \n' + sys.version
    if __name__ == '__main__':
        sys.stderr.write(message + '\n')
        exit(1)
    else:
        raise ImportError(message)

import os
import json 
import builtins
import argparse
from io import StringIO
import base64
import binascii
import json
import traceback
import multiprocessing
from typing import Dict, List, Tuple, Any, Optional, Union, TextIO, NamedTuple

CODE_START_BARRIER = '# CODE AREA {0} #'
BARRIER = '# TEST AREA #'
ENCODING = 'utf8'
TIMEOUT_LIMIT = 5

class InvalidTestFileError(BaseException):
    pass

class TestingError(BaseException):
    pass

class RedirectingResult(NamedTuple):
    stdout: str
    stderr: str
    exception: BaseException
    traceback: traceback.StackSummary

class EvalResult(NamedTuple):
    return_value: Any
    redir: RedirectingResult
    globals: Dict[str, Any]

class TestResult(NamedTuple):
    ok: bool
    message: str

class TestCase(NamedTuple):
    suite_name: str
    case_name: str
    visibility: str
    call: Optional[str]
    result: Optional[str]
    input: Optional[str]
    output: Optional[str]
    exception: Optional[str]
    def __repr__(self):
        return ''

class TestSuite(object):
    name: str
    cases: List[TestCase]
    def __init__(self, suite_name: str):
        self.name = suite_name
        self.cases = []
    def __repr__(self) -> str:
        return ''
    def __eq__(self, other) -> bool:
        return (self.__class__ == other.__class__
            and self.name == other.name
            and self.cases == other.cases)
    def add_case(self, visibility: str, input: Optional[str]=None, output: Optional[str]=None, call: Optional[str]=None, result: Optional[str]=None, exception: Optional[str] = None, case_name: Optional[str] = None) -> TestCase:
        assert isinstance(call, str) or call is None, 'call must be string or None'
        assert isinstance(result, str) or result is None, 'result must be string or None'
        if call is None:
            assert result is None, 'If call is None, result must also be None'
        assert isinstance(input, str) or input is None, 'input must be string or None'
        assert isinstance(output, str) or output is None, 'output must be string or None'
        assert isinstance(exception, str) or exception is None, 'exception must be string or None'
        assert isinstance(case_name, str) or case_name is None, 'case_name must be string or None'
        if case_name is None:
            i = len(self.cases) + 1
            case_name = f'#{i}'
        case = TestCase(self.name, case_name, visibility, call, result, input, output, exception)
        self.cases.append(case)
        return case

class TestPack(Dict[str, TestSuite]):
    current_suite: Optional[TestSuite]
    def __init__(self):
        self.current_suite = None
    def add_suite(self, suite_name: str) -> TestSuite:
        if suite_name in self:
            raise ValueError(f'Cannot add suite "{suite_name}", because a suite with this name is already in this pack.')
        suite = TestSuite(suite_name)
        self[suite_name] = suite
        self.current_suite = suite
        return suite
    def add_case(self, visibility: str, input: Optional[str]=None, output: Optional[str]=None, call: Optional[str]=None, result: Optional[str]=None, exception: Optional[str] = None, case_name: Optional[str] = None) -> TestCase:
        if self.current_suite is None:
            raise ValueError('You must first add a test suite, then you can add test cases.')
        return self.current_suite.add_case(visibility=visibility, input=input, output=output, call=call, result=result, exception=exception, case_name=case_name)
    @property
    def suites(self):
        return list(self.values())

class Redirecting(object):
    def __init__(self, stdin: Optional[str] = None):
        if stdin is None:
            stdin = ''
        self._new_in = StringIO(stdin)
        self._new_out = StringIO()
        self._new_err = StringIO()
        self._new_input_function = FakeInput(self._new_in, self._new_out).input
        self.result = None

    def __enter__(self):
        self._old_in = sys.stdin
        self._old_out = sys.stdout
        self._old_err = sys.stderr
        self._old_input_function = builtins.input
        sys.stdin = self._new_in
        sys.stdout = self._new_out
        sys.stderr = self._new_err
        builtins.input = self._new_input_function
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        sys.stdin = self._old_in
        sys.stdout = self._old_out
        sys.stderr = self._old_err
        builtins.input = self._old_input_function
        self.result = RedirectingResult(self._new_out.getvalue(), self._new_err.getvalue(), ex_value, traceback.extract_tb(ex_traceback))
        self._new_in.close()
        self._new_out.close()
        self._new_err.close()
        return True

class FakeInput(object):
    def __init__(self, stdin: TextIO, stdout: TextIO):
        self.stdin = stdin
        self.stdout = stdout

    def input(self, prompt: str = '') -> str:
        self.stdout.write(prompt)
        line = self.stdin.readline()
        if line == '':
            raise EOFError('Reached the end of the testing input.')
        else:
            return line.rstrip('\n')

class DisablingOpen(object):
    def __enter__(self):
        self._old_open_function = builtins.open
        builtins.open = self.fake_open

    def __exit__(self, ex_type, ex_value, ex_traceback):
        builtins.open = self._old_open_function

    @staticmethod
    def fake_open(*args, **kwargs):
        raise TestingError('Opening files is not allowed in the tested code.')


def load_notebook(filename: str) -> str:
    '''Read Jupyter notebook and return concatenated contents of all code cells. Ignore any lines after the BARRIER.'''
    with open(filename, encoding=ENCODING) as r:
        ntb = json.load(r)
    cells = [cell['source'] for cell in ntb['cells'] if cell['cell_type']=='code']
    all_lines = []
    for cell in cells:
        for line in cell:
            all_lines.append(line.rstrip())
    code = '\n'.join(all_lines)
    if BARRIER not in code:
        raise EOFError(f'Tested notebook must contain a test area starting with "{BARRIER}"')
    code = code.split(BARRIER, maxsplit=1)[0]
    return code

def load_notebook_part(filename: str, part_name: str) -> str:
    code_start_barrier = CODE_START_BARRIER.format(part_name)
    with open(filename, encoding=ENCODING) as r:
        ntb = json.load(r)
    lines = [(line.rstrip('\n'), cell['cell_type']=='code') for cell in ntb['cells'] for line in cell['source']]
    found_part = False
    in_part = False
    code_lines = []
    for cell in ntb['cells']:
        is_code = cell['cell_type']=='code'
        for line in cell['source']:
            line = line.rstrip('\n')
            if code_start_barrier in line:
                found_part = True
                in_part = True
            if BARRIER in line:
                in_part = False
            if in_part and is_code:
                code_lines.append(line)
    if not found_part:
        # return load_notebook(filename)  # DEBUG # TODO remove
        raise TestingError(f'Could not find {code_start_barrier} in {filename}')
    code = '\n'.join(code_lines)
    return code

def remove_test_cells(input_notebook: str, output_notebook: str) -> None:
    with open(input_notebook, encoding=ENCODING) as r:
        ntb = json.load(r)
    out_cells = []
    for cell in ntb['cells']:
        if BARRIER in ''.join(cell['source']):
            pass
        else:
            out_cells.append(cell)
    ntb['cells'] = out_cells
    with open(output_notebook, 'w', encoding=ENCODING) as w:
        json.dump(ntb, w)    

def load_py(filename: str) -> str:
    '''Read .py script and return its contents. Ignore any lines after the BARRIER.'''
    with open(filename, encoding=ENCODING) as r:
        code = r.read()
    if BARRIER in code:
        code = code.split(BARRIER, maxsplit=1)[0]
    return code

def exec_redirected(code: str, *, stdin='', global_vars: Optional[Dict[str, Any]]=None) -> EvalResult:
    '''Execute code, with stdin as the code's standard input, return Redirecting object with the captured outputs.'''
    if global_vars is None:
        global_vars = {}
    with DisablingOpen():
        with Redirecting(stdin=stdin) as redir:
            exec(code, global_vars)
    return EvalResult(None, redir.result, global_vars)

def eval_redirected(code: str, *, stdin='', global_vars: Optional[Dict[str, Any]]=None) -> EvalResult:
    '''Execute code, with stdin as the code's standard input, return Redirecting object with the captured outputs.'''
    if global_vars is None:
        global_vars = {}
    return_value = None
    with DisablingOpen():
        with Redirecting(stdin=stdin) as redir:
            return_value = eval(code, global_vars)
    return EvalResult(return_value, redir.result, global_vars)

def apply(func_args_kwargs):
    func, args, kwargs = func_args_kwargs
    return func(*args, **kwargs)

def apply_with_timeout(func_args_kwargs, timeout_limit=TIMEOUT_LIMIT):
    '''Run func(*args, **kwargs) and return its return value, or result_on_timeout if it does not return in timeout_limit (in seconds).'''
    with multiprocessing.Pool(1) as pool:
        result_iterator = pool.imap(apply, [func_args_kwargs], chunksize=1)
        try:
            return result_iterator.next(TIMEOUT_LIMIT)
        except multiprocessing.TimeoutError:
            raise TimeoutError(f'Exceeded time limit ({timeout_limit} seconds).')

def fmt_tb(tb, code, skip_first = 0) -> List[str]:
    code_lines = code.split('\n')
    result = []
    tb_list = tb
    for file, lineno, fction, line in tb_list[skip_first:]:
        if line == '':
            try:
                line = code_lines[lineno-1]
            except:
                pass
        result.append((file, lineno, fction, line))
    tb_lines = traceback.format_list(result) # type: ignore
    return tb_lines

def fmt_exception(exception, tb, code, show_message=True, skip_first=0) -> List[str]:
    tb_lines = fmt_tb(tb, code, skip_first=skip_first)
    if show_message:
        ex_lines = traceback.format_exception_only(type(exception), exception)
    else:
        ex_lines = [f'{type(exception).__name__} (details hidden)\n']
    lines = ['Traceback (most recent call last):\n', *tb_lines, *ex_lines]
    return lines

def is_nofloat_type(value) -> bool:
    BASIC_TYPES = (str, bytes, int, bool, type, BaseException, type(None))
    if isinstance(value, BASIC_TYPES):
        return True
    elif isinstance(value, (list, tuple, set)) and all(is_nofloat_type(item) for item in value):
        return True
    elif isinstance(value, dict) and all(is_nofloat_type(k) for k in value.keys()) and all(is_nofloat_type(v) for v in value.values()):
        return True
    else:
        return False

def soft_equal(refval, value, float_tolerance=1e-6) -> bool:
    if is_nofloat_type(value):
        return refval == value
    elif isinstance(refval, float):
        return isinstance(value, (float, int)) and abs(refval - value) <= float_tolerance
    elif type(refval) != type(value):
        return False
    elif isinstance(refval, (list, tuple)):
        return len(refval) == len(value) and all(soft_equal(x, y) for x, y in zip(refval, value))
    elif isinstance(refval, dict) and all(is_nofloat_type(key) for key in refval.keys()):
        return set(refval.keys()) == set(value.keys()) and all(refval[key] == value[key] for key in refval.keys())
    else:
        raise NotImplementedError(f'soft_equal() not implemented for {value}')

def run_test_case(case: TestCase, code: str, timeout_limit: Optional[float] = None) -> TestResult:
    if timeout_limit is None:
        if case.call is None:
            return run_test_case_io(case, code)
        else:
            return run_test_case_func(case, code)
    else:
        try:
            return apply_with_timeout((run_test_case, [case, code], {}), timeout_limit=timeout_limit)
        except TimeoutError as err:
            message = f'Test {case.case_name} failed - {err}'
            return TestResult(False, message)

def run_test_case_io(case: TestCase, code: str) -> TestResult:
    '''Execute code and compare it's standard output with expected_output'''
    result = exec_redirected(code, stdin=case.input)
    if result.redir.exception is not None:
        if type(result.redir.exception).__name__ == case.exception:
            lines = [f'Test {case.case_name} passed']
            return TestResult(ok=True, message='\n'.join(lines))
        else:
            lines = [f'Test {case.case_name} failed - exception occurred']
            if case.visibility == 'open':
                tb = fmt_exception(result.redir.exception, result.redir.traceback, code, skip_first=1)
            else:
                tb = fmt_exception(result.redir.exception, result.redir.traceback, code, show_message=False, skip_first=1)
            lines.extend(['', ''.join(tb)])
            return TestResult(ok=False, message='\n'.join(lines))
    elif case.exception is not None:
        lines = [f'Test {case.case_name} failed - should raise {case.exception}']
        if case.visibility == 'open':
            lines.extend(['', 'Test input:', case.input or ''])
        else:
            lines.extend(['(details hidden)'])
        return TestResult(ok=False, message='\n'.join(lines))
    elif case.output is not None and rstrip_lines(case.output) != rstrip_lines(result.redir.stdout):
        lines = [f'Test {case.case_name} failed - wrong output']
        if case.visibility == 'open':
            lines.extend([
                '', 'Test input:', case.input or '', 
                '', 'Correct output:', case.output,
                '', 'Your output:', result.redir.stdout
            ])
        else:
            lines.extend(['(details hidden)'])
        return TestResult(ok=False, message='\n'.join(lines))
    return TestResult(ok=True, message=f'Test {case.case_name} passed')

def run_test_case_func(case: TestCase, code: str) -> TestResult:
    definitions: Dict[str, Any] = {}
    def_result = exec_redirected(code, global_vars=definitions)
    if def_result.redir.exception is not None:
        lines = fmt_exception(def_result.redir.exception, def_result.redir.traceback, code, skip_first=1)
        return TestResult(ok=False, message='\n'.join(lines))
    else:
        call_result = eval_redirected(case.call, global_vars=definitions, stdin=case.input)
        if call_result.redir.exception is not None:
            if type(call_result.redir.exception).__name__ == case.exception:
                return TestResult(ok=True, message=f'Test {case.case_name} passed')
            else:
                lines = [f'Test {case.case_name} failed - exception occurred']
                if case.visibility == 'open':
                    tb = fmt_exception(call_result.redir.exception, call_result.redir.traceback, code, skip_first=2)
                else:
                    tb = fmt_exception(call_result.redir.exception, call_result.redir.traceback, code, show_message=False, skip_first=2)
                lines.extend(['', ''.join(tb)])
                return TestResult(ok=False, message='\n'.join(lines))
        if case.exception is not None:
            lines = [f'Test {case.case_name} failed - should raise {case.exception}']
            if case.visibility == 'open':
                lines.extend(['', 'Test call:', case.call])
                if case.input is not None:
                    lines.extend(['', 'Test input:', case.input])
            else:
                lines.extend(['(details hidden)'])
            return TestResult(ok=False, message='\n'.join(lines))
        if case.result is not None and not soft_equal(eval(case.result), call_result.return_value):
            lines = [f'Test {case.case_name} failed - wrong return value']
            if case.visibility == 'open':
                lines.extend(['', 'Test call:', case.call])
                if case.input is not None:
                    lines.extend(['', 'Test input:', case.input])
                lines.extend(['', 'Correct return value:', case.result])
                lines.extend(['', 'Your return value:', repr(call_result.return_value)])
            else:
                lines.extend(['(details hidden)'])
            return TestResult(ok=False, message='\n'.join(lines))
        if case.output is not None and rstrip_lines(case.output) != rstrip_lines(call_result.redir.stdout):
            lines = [f'Test {case.case_name} failed - wrong output']
            if case.visibility == 'open':
                lines.extend(['', 'Test call:', case.call])
                if case.input is not None:
                    lines.extend(['', 'Test input:', case.input])
                lines.extend(['', 'Correct output:', case.output])
                lines.extend(['', 'Your output:', call_result.redir.stdout])
            else:
                lines.extend(['(details hidden)'])
            return TestResult(ok=False, message='\n'.join(lines))
        return TestResult(ok=True, message=f'Test {case.case_name} passed')

def rstrip_lines(text: str) -> str:
    lines = text.rstrip().split('\n')
    result = '\n'.join(line.rstrip() for line in lines)
    return result

def run_test_suite(suite: TestSuite, code: str) -> TestResult:
    for case in suite.cases:
        result = run_test_case(case, code, timeout_limit=TIMEOUT_LIMIT)
        if not result.ok:
            return result
    return TestResult(True, 'Tests passed :)')


def encode_obj(obj: object) -> bytes:
    string = json.dumps(obj)
    check = json.loads(string)
    if check != obj:
        raise ValueError(f'Could not encode object: {obj}')
    return base64.encodebytes(string.encode(ENCODING))

def decode_obj(enc_obj: bytes) -> object:
    string = base64.decodebytes(enc_obj).decode(ENCODING)
    return json.loads(string)

def encode_test_case(case: TestCase) -> bytes:
    enc_fields = b' '.join(encode_obj(f) for f in case)
    return base64.encodebytes(enc_fields)

def decode_test_case(enc_case: bytes) -> TestCase:
    enc_fields = base64.decodebytes(enc_case)
    fields: list = [decode_obj(f) for f in enc_fields.split(b' ')]
    return TestCase(*fields)

def simple_hash(message: bytes) -> bytes:
    n = sum(message)
    return base64.encodebytes(str(n).encode(ENCODING))

def check_simple_hash(message: bytes, hash: bytes) -> bool:
    return simple_hash(message) == hash

def encode_tests(tests: TestPack) -> bytes:
    enc_cases = []
    for suite in tests.suites:
        for case in suite.cases:
            enc_cases.append(encode_test_case(case))
    together = b' '.join(enc_cases)
    return base64.encodebytes(simple_hash(together) + b' ' + together)
    
def decode_tests(tests: bytes) -> TestPack:
    tests = base64.decodebytes(tests)
    if b' ' not in tests:
        raise InvalidTestFileError('Invalid test file')
    h, together = tests.split(b' ', 1)
    if not check_simple_hash(together, h):
        raise InvalidTestFileError('Invalid test file')
    cases = [decode_test_case(c) for c in together.split(b' ')]
    pack = TestPack()
    for case in cases:
        suite_name = case.suite_name
        if suite_name not in pack:
            pack.add_suite(suite_name)
        pack[suite_name].cases.append(case)
    return pack

def save_tests(tests: TestPack, filename: str) -> None:
    content = encode_tests(tests)
    with open(filename, 'wb') as w:
        w.write(content)
    check = load_tests(filename)
    if check != tests:
        raise ValueError(f'Could not encode tests: {tests}')

def load_tests(filename: str) -> TestPack:
    try:
        with open(filename, 'rb') as r:
            content = r.read()
        tests = decode_tests(content)
        return tests
    except OSError:
        raise InvalidTestFileError(f'Cannot read test file "{filename}". Make sure you did not remove or rename this file.')
    except binascii.Error:
        raise InvalidTestFileError(f'Invalid test file "{filename}". Make sure you did not modify this file.')
    
def load_suite(test_file: str, suite_name: str) -> TestSuite:
    tests = load_tests(test_file)
    try:
        return tests[suite_name]
    except KeyError:
        raise InvalidTestFileError(f'Test suite {suite_name} not found')

def print_error(error: Union[str, BaseException]) -> None:
    print('ERROR:', error, end='\n\n', file=sys.stderr)

def run_tests_(notebook: str, test_suite: Optional[str] = None, test_file: Optional[str] = None) -> bool:
    '''Run all tests in suite test_suite in test_file on the merged code cells in notebook. 
    Default test_suite is the notebook name without extension.
    Default test_file is dirname(notebook)/tests.xxx.
    Return True iff all tests pass.'''
    ntb_name, ntb_ext = os.path.splitext(os.path.basename(notebook))
    if test_suite is None:
        test_suite = ntb_name
    if test_file is None:
        test_file = os.path.join(os.path.dirname(notebook), 'tests.xxx')
    try:
        if ntb_ext == '.ipynb':
            try:
                code = load_notebook_part(notebook, test_suite)
            except TestingError as ex:
                print_error(ex)
                return False
        elif ntb_ext == '.py':
            code = load_py(notebook)
        else:
            print_error(f'Tested file must have extension .ipynb or .py')
            return False
    except OSError:
        print_error(f'Cannot read file "{notebook}". Make sure you did not rename the notebook.')
        return False
    except EOFError as ex:
        print_error(ex)
        return False
    try:
        suite = load_suite(test_file, test_suite)
    except InvalidTestFileError as ex:
        print_error(ex)
        return False
    try:
        result = run_test_suite(suite, code)
    except TestingError as ex:
        print_error(ex)
        return False
    print(result.message)
    return result.ok

def run_tests(notebook: str, test_suite: Optional[str] = None, test_file: Optional[str] = None) -> None:
    '''Run all tests in suite test_suite in test_file on the merged code cells in notebook. 
    Default test_suite is the notebook name without extension.
    Default test_file is dirname(notebook)/tests.xxx.'''
    run_tests_(notebook, test_suite=test_suite, test_file=test_file)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Jupyter Notebook (.ipynb) or Python script (.py) to be tested.', type=str)
    parser.add_argument('-s', '--test_suite', help='Name of the test suite to run.', type=str)
    parser.add_argument('-f', '--test_file', help='Path to the test file (default: tests.xxx).', type=str)
    args = parser.parse_args()
    success = run_tests_(args.input, test_suite=args.test_suite, test_file=args.test_file)
    return 0 if success else 1

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
