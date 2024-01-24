import json
import os

def read_file(file):
    """
    Reads the contents of a file and returns them as a string.

    Args:
        file (str): The path to the file that needs to be read.

    Returns:
        str: The contents of the file as a string.
    """
    file = open(file, "r")
    data = file.read()
    file.close()
    return data

def write_json_file(data, filename):
    """
    Writes data to a JSON file.

    Args:
        data (dict): The data to be written to a JSON file.
        filename (str): The path to the JSON file.
    """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def read_json_file(filename):
    """
    Reads data from a JSON file.
    Replaces "Infinity" strings with float("inf").
    Replaces "-Infinity" strings with -float("inf").

    Args:
        filename (str): The path to the JSON file.

    Returns:
        dict: The data read from the JSON file as a dictionary. If an exception occurs, returns None.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except:
        return None

def get_absolute_path(relative_path):
    #current_directory = os.path.dirname(os.path.abspath(__file__))
    #return os.path.join(current_directory, relative_path)
    return os.path.relpath(relative_path)

def get_relative_path_if_in_cwd(path):
    current_directory = os.getcwd()
    if os.path.commonpath([path, current_directory]) == current_directory:
        return os.path.relpath(path, current_directory)
    return path

