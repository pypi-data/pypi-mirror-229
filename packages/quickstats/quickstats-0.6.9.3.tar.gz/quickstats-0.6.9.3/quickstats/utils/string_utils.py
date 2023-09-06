from typing import Optional, Callable
import re

def split_lines(s: str, comment_string: Optional[str] = "#", remove_blank: bool = True,
                with_line_number: bool = False, keepends: bool = False):
    """
    Split a multi-line string into individual lines and optionally remove comments and/or blank lines.

    Parameters:
        s (str): The input multi-line string to be split.
        comment_string (Optional[str], optional): The string representing the start of a comment line.
                                                  Lines starting with this string will be considered as comments 
                                                  and removed. Defaults to "#".
        remove_blank (bool, optional): If True, remove blank lines (lines containing only whitespace).
                                       Defaults to True.
        with_line_number (bool, optional): If True, returns a list of tuples with line numbers and lines.
                                           If False, returns a list of lines. Defaults to False.
        keepends (bool, optional): If True, the line breaks are included in each line. If False, line breaks 
                                   are removed. Defaults to False.

    Returns:
        list or list of tuples: A list of lines from the input string. If 'with_line_number' is True, 
                                it returns a list of tuples with line numbers and lines.
    """
    lines = s.splitlines(keepends=keepends)

    if comment_string:
        lines = [line.split(comment_string, 1)[0] for line in lines]

    if remove_blank and with_line_number:
        lines = [(line, i + 1) for i, line in enumerate(lines) if line.strip()]
    elif remove_blank:
        lines = [line for line in lines if line.strip()]
    elif with_line_number:
        lines = [(line, i + 1) for i, line in enumerate(lines)]
        
    return lines


def split_str(s: str, sep: str = None, strip: bool = True, remove_empty: bool = False, cast: Optional[Callable] = None) -> list:
    """
    Splits a string and applies optional transformations.

    This function splits a string into a list where each element is a substring of the 
    original string. By default, it trims leading and trailing whitespace from each substring. 
    It can also optionally remove empty substrings and apply a casting function to each substring.

    Parameters
    ----------
    s : str
        The string to split.
    sep : str, optional
        The separator according to which the string is split. If not specified or None, 
        the string is split at any whitespace. Defaults to None.
    strip : bool, optional
        Whether to trim leading and trailing whitespace from each substring. Defaults to True.
    remove_empty : bool, optional
        Whether to remove empty substrings from the list. Defaults to False.
    cast : Callable, optional
        An optional casting function to apply to each substring. It should be a function 
        that takes a single string argument and returns a value. Defaults to None.

    Returns
    -------
    list
        A list of substrings (or transformed substrings) obtained by splitting the input string.
    """
    items = s.split(sep)
    if strip:
        items = [item.strip() for item in items]
    if remove_empty:
        items = [item for item in items if item]
    if cast is not None:
        items = [cast(item) for item in items]
    return items

whitespace_trans = str.maketrans('', '', " \t\r\n\v")
newline_trans = str.maketrans('', '', "\r\n")

def remove_whitespace(s: str) -> str:
    """
    Removes all whitespace characters from a string.

    The function effectively removes characters like space, tab, carriage return, 
    newline, and vertical tab from the provided string.

    Parameters
    ----------
    s : str
        The input string from which to remove whitespace.

    Returns
    -------
    str
        The string with all whitespace characters removed.
    """
    return s.translate(whitespace_trans)

def remove_newline(s: str):
    """
    Removes newline characters from a string.

    Parameters:
        s (str): The input string from which to remove newline characters.

    Returns:
        str: The input string with all newline characters removed.
    """
    return s.translate(newline_trans)

neg_zero_regex = re.compile(r'(?![\w\d])-(0.[0]+)(?![\w\d])')

def remove_neg_zero(s:str):
    """
    Replaces instances of negative zero in a string with zero.
    
    Parameters:
        string (str): The input string in which to replace negative zeros.

    Returns:
        str: The input string with all instances of negative zero replaced with zero.

    Example:
        string = "The temperature is -0.000 degrees."
        print(remove_neg_zero(string))
        # outputs: "The temperature is 0.000 degrees."
    """
    return neg_zero_regex.sub(r'\1', s)