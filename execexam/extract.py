"""Extract contents from data structures."""

import ast
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

from . import convert


def is_failing_test_details_empty(details: str) -> bool:
    """Determine if the string contains a newline as a hallmark of no failing tests."""
    if details == "\n":
        return True
    return False


def extract_details(details: Dict[Any, Any]) -> str:
    """Extract the details of a dictionary and return it as a string."""
    output = []
    # iterate through the dictionary and add each key-value pair
    for key, value in details.items():
        output.append(f"{value} {key}")
    if len(output) == 0:
        return ""
    return "Details: " + ", ".join(output)


def extract_test_run_details(details: Dict[Any, Any]) -> str:
    """Extract the details of a test run."""
    # Format of the data in the dictionary:
    # 'summary': Counter({'passed': 2, 'total': 2, 'collected': 2})
    summary_details = details["summary"]
    # convert the dictionary of summary to a string
    summary_details_str = extract_details(summary_details)
    return summary_details_str


def extract_test_assertion_details(test_details: Dict[Any, Any]) -> str:
    """Extract the details of a dictionary and return it as a string."""
    # create an empty list to store the output
    output = []
    # indicate that this is the first assertion
    # to be processed (it will have a "-" to start)
    first = True
    # iterate through the dictionary and add each key-value pair
    # that contains the details about the assertion
    for key, value in test_details.items():
        # this is the first assertion and thus
        # the output will start with a "-"
        if first:
            output = ["  - "]
            output.append(f"{key}: {value}\n")
            first = False
        # this is not the first assertion and thus
        # the output will start with a "  " to indent
        else:
            output.append(f"    {key}: {value}\n")
    # return each index in the output list as a string
    return "".join(output)


def extract_test_assertion_details_list(details: List[Dict[Any, Any]]) -> str:
    """Extract the details of a list of dictionaries and return it as a string."""
    output = []
    # iterate through the list of dictionaries and add each dictionary
    # to the running string that conatins test assertion details
    for current_dict in details:
        output.append(extract_test_assertion_details(current_dict))
    return "".join(output)


def extract_test_assertions_details(test_reports: List[dict[str, Any]]):
    """Extract the details of test assertions."""
    # create an empty list that will store details about
    # each test case that was execued and each of
    # the assertions that was run for that test case
    test_report_string = ""
    # iterate through the list of test reports
    # where each report is a dictionary that includes
    # the name of the test and the assertions that it ran
    for test_report in test_reports:
        # get the name of the test
        test_name = test_report["nodeid"]
        # extract only the name of the test file and the test name,
        # basically all of the content after the final slash
        display_test_name = test_name.rsplit("/", 1)[-1]
        test_report_string += f"\n{display_test_name}\n"
        # there is data about the assertions for this
        # test and thus it should be extracted and reported
        if "assertions" in test_report:
            test_report_string += extract_test_assertion_details_list(
                test_report["assertions"]
            )
    # return the string that contains all of the test assertion details
    return test_report_string


def extract_failing_test_details(
    details: dict[Any, Any],
) -> Tuple[str, List[Dict[str, Path]]]:
    """Extract the details of a failing test."""
    # extract the tests from the details
    tests = details["tests"]
    # create an empty string that starts with a newline;
    # the goal of the for loop is to incrementally build
    # of a string that contains all deteails about failing tests
    failing_details_str = "\n"
    # create an initial path for the file containing the failing test
    failing_test_paths = []
    # incrementally build up results for all of the failing tests
    for test in tests:
        if test["outcome"] == "failed":
            current_test_failing_dict = {}
            # convert the dictionary of failing details to a string
            # and add it to the failing_details_str
            failing_details = test
            # get the nodeid of the failing test
            failing_test_nodeid = failing_details["nodeid"]
            failing_details_str += f"  Name: {failing_test_nodeid}\n"
            # get the call information of the failing test
            failing_test_call = failing_details["call"]
            # get the crash information of the failing test's call
            failing_test_crash = failing_test_call["crash"]
            # extract the root of the report, which corresponds
            # to the filesystem on which the tests were run
            failing_test_path_root = details["root"]
            # extract the name of the file that contains the test
            # from the name of the individual test case itself
            failing_test_nodeid_split = failing_test_nodeid.split("::")
            # create a complete path to the file that contains the failing test file
            failing_test_path = (
                Path(failing_test_path_root) / failing_test_nodeid_split[0]
            )
            # extract the name of the function from the nodeid
            failing_test_name = failing_test_nodeid_split[-1]
            # assign the details about the failing test to the dictionary
            current_test_failing_dict["test_name"] = failing_test_name
            current_test_failing_dict["test_path"] = failing_test_path
            failing_test_paths.append(current_test_failing_dict)
            # creation additional diagnotics about the failing test
            # for further display in the console in a text-based fashion
            failing_test_path_str = convert.path_to_string(
                failing_test_path, 4
            )
            failing_test_lineno = failing_test_crash["lineno"]
            failing_test_message = failing_test_crash["message"]
            # assemble all of the failing test details into the string
            failing_details_str += f"  Path: {failing_test_path_str}\n"
            failing_details_str += f"  Line number: {failing_test_lineno}\n"
            failing_details_str += f"  Message: {failing_test_message}\n"
    # return the string that contains all of the failing test details
    return (failing_details_str, failing_test_paths)


def extract_test_output(keep_line_label: str, output: str) -> str:
    """Filter the output of the test run to keep only the lines that contain the label."""
    # create an empty string that will store the filtered output
    filtered_output = ""
    # iterate through the lines in the output
    for line in output.splitlines():
        # if the line contains the label, add it to the filtered output
        if keep_line_label in line:
            filtered_output += line + "\n"
    # return the filtered output
    return filtered_output


def extract_test_output_multiple_labels(
    keep_line_labels: List[str], output: str
) -> str:
    """Filter the output of the test run to keep only the lines that contain the label."""
    # create an empty string that will store the filtered output
    filtered_output = ""
    # iterate through the lines in the output
    for line in output.splitlines():
        # if the line contains any one of the the labels,
        # then add it to the filtered output
        if any(label in line for label in keep_line_labels):
            filtered_output += line + "\n"
    # return the filtered output
    return filtered_output


# def extract_failing_implementation_code(json_report: Dict[Any, Any], debug: bool = True) -> Optional[str]:
#     """Extract the source code of the failing implementation from pytest's JSON report."""
#     # Make a function for printing debug statments
#     def debug_print(msg: str) -> None:
#         if debug:
#             print(f"DEBUG: {msg}")
#     # If the report is empty it means no tests were found
#     if not json_report or 'tests' not in json_report:
#         debug_print("No tests found in JSON report")
#         return None    
#     # Find the first failing test
#     failing_tests = [test for test in json_report['tests'] 
#                     if test.get('outcome') in ('failed', 'error')]
#     if not failing_tests:
#         debug_print("No failing tests found")
#         return None  
#     # MAKE IT SO IT GOES THROUGH MULTIPLE TESTS 
#     failing_test = failing_tests[0]
#     debug_print(f"Found failing test: {failing_test.get('nodeid', '')}")
#     # Extract traceback information from the test failure
#     if 'call' in failing_test and 'traceback' in failing_test['call']:
#         traceback_entries = failing_test['call']['traceback']
#         debug_print(f"Found {len(traceback_entries)} traceback entries")
        
#         for entry in traceback_entries:
#             # Look for the actual source file where the error occurred
#             path = entry.get('path')
#             lineno = entry.get('lineno')
#             debug_print(f"Examining traceback entry: {path}:{lineno}")
#             if path and not any(x in path for x in ['test_', 'pytest', 'site-packages', 'lib']):
#                 debug_print(f"Found potential implementation file: {path}")
#                 try:
#                     with open(path, 'r') as f:
#                         content = f.read()
#                     # Parse the file to find the function containing the error line
#                     tree = ast.parse(content)
#                     for node in ast.walk(tree):
#                         if isinstance(node, ast.FunctionDef):
#                             # Check if this function contains the error line
#                             if node.lineno <= lineno <= node.end_lineno:
#                                 func_source = '\n'.join(
#                                     content.splitlines()[node.lineno-1:node.end_lineno]
#                                 )
#                                 debug_print(f"Found function containing error: {node.name}")
#                                 return func_source
#                 except Exception as e:
#                     debug_print(f"Error processing file {path}: {e}")
#                     continue
#     # If it couldn't find the source through traceback, try to find the function name
#     # from the test name and search all Python files in the project
#     debug_print("Trying to find source through test name...")
#     test_name = failing_test.get('nodeid', '').split('::')[-1]
#     if test_name.startswith('test_'):
#         func_name = test_name[5:]  # Remove 'test_' prefix
#         debug_print(f"Looking for implementation of: {func_name}")
#         # Start from the test file's directory and search upwards
#         test_path = Path(failing_test.get('nodeid', '').split('::')[0])
#         current_dir = test_path.parent
#         # Look up to 3 directory levels
#         for _ in range(3): 
#             debug_print(f"Searching in directory: {current_dir}")
#             for py_file in current_dir.rglob('*.py'):
#                 if 'test_' not in py_file.name and py_file.is_file():
#                     debug_print(f"Examining file: {py_file}")
#                     try:
#                         with open(py_file, 'r') as f:
#                             content = f.read()
#                         tree = ast.parse(content)
#                         for node in ast.walk(tree):
#                             if isinstance(node, ast.FunctionDef) and node.name == func_name:
#                                 func_source = '\n'.join(
#                                     content.splitlines()[node.lineno-1:node.end_lineno]
#                                 )
#                                 debug_print(f"Found matching function in {py_file}")
#                                 return func_source
#                     except Exception as e:
#                         debug_print(f"Error examining file {py_file}: {e}")
#                         continue
#             current_dir = current_dir.parent
#     debug_print("Could not find implementation code")
#     return None

def extract_failing_implementation_code(json_report: Dict[Any, Any], debug: bool = True) -> Optional[List[str]]:
    """Extract the source code of the failing implementation from pytest's JSON report."""
    # Make a function for printing debug statments
    def debug_print(msg: str) -> None:
        if debug:
            print(f"DEBUG: {msg}")
    # If the report is empty it means no tests were found
    failing_functions = []
    if not json_report or 'tests' not in json_report:
        debug_print("No tests found in JSON report")
        return None    
    # Find the first failing test
    failing_tests = [test for test in json_report['tests'] 
                    if test.get('outcome') in ('failed', 'error')]
    if not failing_tests:
        debug_print("No failing tests found")
        return None  
    # MAKE IT SO IT GOES THROUGH MULTIPLE TESTS
    for failing_test in failing_tests:
    # failing_test = failing_tests[0]
        debug_print(f"Found failing test: {failing_test.get('nodeid', '')}")
        # Extract traceback information from the test failure
        if 'call' in failing_test and 'traceback' in failing_test['call']:
            traceback_entries = failing_test['call']['traceback']
            debug_print(f"Found {len(traceback_entries)} traceback entries")
            for entry in traceback_entries:
                # Look for the actual source file where the error occurred
                path = entry.get('path')
                lineno = entry.get('lineno')
                debug_print(f"Examining traceback entry: {path}:{lineno}")
                if path and not any(x in path for x in ['test_', 'pytest', 'site-packages', 'lib']):
                    debug_print(f"Found potential implementation file: {path}")
                    try:
                        with open(path, 'r') as f:
                            content = f.read()
                        # Parse the file to find the function containing the error line
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                # Check if this function contains the error line
                                if node.lineno <= lineno <= node.end_lineno:
                                    func_source = '\n'.join(
                                        content.splitlines()[node.lineno-1:node.end_lineno]
                                    )
                                    debug_print(f"Found function containing error: {node.name}")
                                    if func_source not in failing_functions:
                                        failing_functions.append(func_source)
                    except Exception as e:
                        debug_print(f"Error processing file {path}: {e}")
                        continue
        # If it couldn't find the source through traceback, try to find the function name
        # from the test name and search all Python files in the project
        debug_print("Trying to find source through test name...")
        test_name = failing_test.get('nodeid', '').split('::')[-1]
        if test_name.startswith('test_'):
            func_name = test_name[5:]  # Remove 'test_' prefix
            debug_print(f"Looking for implementation of: {func_name}")
            # Start from the test file's directory and search upwards
            test_path = Path(failing_test.get('nodeid', '').split('::')[0])
            current_dir = test_path.parent
            # Look up to 3 directory levels
            for _ in range(3): 
                debug_print(f"Searching in directory: {current_dir}")
                for py_file in current_dir.rglob('*.py'):
                    if 'test_' not in py_file.name and py_file.is_file():
                        debug_print(f"Examining file: {py_file}")
                        try:
                            with open(py_file, 'r') as f:
                                content = f.read()
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                                    func_source = '\n'.join(
                                        content.splitlines()[node.lineno-1:node.end_lineno]
                                    )
                                    debug_print(f"Found matching function in {py_file}")
                                    if func_source not in failing_functions:
                                        failing_functions.append(func_source)
                                    #return func_source
                        except Exception as e:
                            debug_print(f"Error examining file {py_file}: {e}")
                            continue
                current_dir = current_dir.parent
        if len(failing_functions) is not 0:
            debug_print("Successfully found failing functions")
            return failing_functions 
        debug_print("Could not find implementation code")
        return None