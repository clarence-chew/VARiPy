def parse_command(command_string):
    """
    Parses a command string and returns a list of arguments.

    Args:
        command_string (str): The input command string that needs to be parsed.

    Returns:
        list: A list of parsed arguments extracted from the input command string.
    """
    arguments = []
    current_argument = []
    quote_type = ""
    # obtain commands by looping
    for idx, char in enumerate(command_string):
        if char in ('"', "'", "`"):
            if not quote_type:
                # escape quotes by doubling
                if idx and command_string[idx-1] == char:
                    arguments.append("".join(char))
                quote_type = char
            elif char == quote_type:
                quote_type = ""
            else:
                current_argument.append(char)
        elif char == " " and not quote_type:
            if current_argument:
                arguments.append("".join(current_argument))
                current_argument = []
        else:
            current_argument += char
    # input last command
    if current_argument:
        arguments.append("".join(current_argument))
    return arguments