import json

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

def subdictionary(dictionary, keys):
    """
    Gets a smaller dictionary with only specified keys.

    Args:
        dictionary (dict): The dictionary from which a subdictionary needs to be extracted.
        keys (list): The list of keys to include in the subdictionary.

    Returns:
        dict: A new dictionary containing only the specified keys from the original dictionary.
    """
    return {key: dictionary[key] for key in keys if key in dictionary}

def constrain(value, min_val, max_val):
    """
    Constrains a value within a given range.

    Args:
        value (numeric): The value to be constrained.
        min_val (numeric): The minimum value for the constraint.
        max_val (numeric): The maximum value for the constraint.

    Returns:
        numeric: The constrained value.
    """
    return max(min_val, min(max_val, value))

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
