"""Extract contents from data structures."""

import ast
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Union

import sys 
import os
from . import convert
import subprocess
import inspect
import importlib.util


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

def extract_imports_from_test(test_file: str) -> List[str]:
    """Extract import statements from a given test file using AST."""
    with open(test_file, 'r') as file:
        tree = ast.parse(file.read(), filename=test_file)
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module is not None:
                imports.append(module)
    
    return imports

def resolve_import_path(module_name: str, test_file_path: str) -> Optional[Path]: 
    """Try to resolve the import path to a source file."""
    try:
        # Resolve relative imports based on the test file location
        test_dir = os.path.dirname(test_file_path)
        sys.path.insert(0, test_dir)
        
        # Attempt to locate the module
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            return spec.origin
    except ImportError:
        pass
    finally:
        sys.path.pop(0)
    
    return None

def find_source_file(root_dir: Path, function_name: str) -> Path:
    """Recursively search for the source file containing the function definition."""
    print(f"Searching for the source file containing the function: {function_name}")
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = Path(dirpath) / filename
                with open(file_path, "r", encoding="utf-8") as source_file:
                    try:
                        source_tree = ast.parse(source_file.read())
                        for node in ast.walk(source_tree):
                            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                                print(f"Found function '{function_name}' in file: {file_path}")
                                return file_path
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

    raise FileNotFoundError(f"Source file containing function '{function_name}' not found in {root_dir}.")


def get_source_file_from_test(test_file_path: str) -> Optional[Path]:
    """Extract imports and attempt to find the source code."""
    imports = extract_imports_from_test(test_file_path)
    
    source_files = []
    for module in imports:
        source_path = resolve_import_path(module, test_file_path)
        if source_path:
            source_files.append(source_path)
    
    return source_files

def extract_tested_function(test_name: Path, test_file_path: Path, project_root: Path) -> str:
    """Extract the code of the function being tested and automatically locate the source file."""
    print(f"Processing test file: {test_file_path}")

    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file not found: {test_file_path}")

    # Parse the test file to get the AST tree
    with open(test_file_path, "r", encoding="utf-8") as test_file:
        test_tree = ast.parse(test_file.read())

    function_calls = []

    # Walk through the AST nodes and collect all function calls
    for node in ast.walk(test_tree):
        if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
            function_calls.append(node)

    if not function_calls:
        print("No function calls found in the test file.")
        return None

    # Assuming the first function call is the one being tested
    tested_function_name = function_calls[0].func.id
    print(f"Tested function found: {tested_function_name}")

    # Automatically find the source file containing the function definition
    source_file_path = find_source_file(project_root, tested_function_name)

    print(f"Source file found at: {source_file_path}")

    # Parse the source file to get the AST tree
    try:
        with open(source_file_path, "r", encoding="utf-8") as source_file:
            source_tree = ast.parse(source_file.read())
    except Exception as e:
        print(f"Failed to open source file: {e}")
        raise

    # Further processing of the source_tree can be done here...

    return tested_function_name