from typing import Union
import numpy as np


def split_list_of_strings_at_indices(
    strings: Union[list, tuple, np.ndarray], splitlist: Union[list, tuple, np.ndarray]
) -> np.ndarray:
    r"""
    Splits a list of strings at specified character indices.

    :param strings: List of strings to be split.
    :type strings: Union[list, tuple, np.ndarray]

    :param splitlist: List of indices at which to split the strings.
    :type splitlist: Union[list, tuple, np.ndarray]

    :return: 2D NumPy array where each row contains the split strings.
    :rtype: np.ndarray

    Example usage:
    >>> from stringindexsplit import split_list_of_strings_at_indices
    >>> stringlist = '''For most Unix systems, you must download and compile the source code. The same source code archive can also be used to build the Windows and Mac versions, and is the starting point for ports to all other platforms.'''.split()
    >>> splist = split_list_of_strings_at_indices(
    ...     stringlist,
    ...     splitlist=(
    ...         0,
    ...         2,
    ...         3,
    ...         6,
    ...         7,
    ...     ),
    ... )
    >>> print(splist)

    [['Fo' 'r' '' '' '']
     ['mo' 's' 't' '' '']
     ['Un' 'i' 'x' '' '']
     ['sy' 's' 'tem' 's' ',']
     ['yo' 'u' '' '' '']
     ['mu' 's' 't' '' '']
     ['do' 'w' 'nlo' 'a' 'd']
     ['an' 'd' '' '' '']
     ['co' 'm' 'pil' 'e' '']]
    """
    if not isinstance(strings, np.ndarray):
        strings = np.array(strings)

    # Convert to Unicode if not already
    a5 = strings.astype("U")

    # Reshape the strings for splitting
    a6 = np.char.array(a5).view("S1").reshape((a5.shape[0], a5.itemsize, -1)).squeeze()

    # Initialize a list to store the split strings
    splia = []

    # Copy the splitlist to avoid modifying the original
    splitliste = list(splitlist).copy()

    # Ensure the first split starts at 0
    if splitliste[0] != 0:
        splitliste.insert(0, 0)

    # Ensure the last split extends to the end of the string
    if splitliste[-1] < (g := len(a6[1]) // 4):
        splitliste.append(g)

    # Split the strings and store them in the list
    for sp0, sp1 in zip(splitliste, splitliste[1:]):
        disa = sp1 - sp0
        splia.append(a6[..., sp0 * 4 : sp1 * 4].view(f"U{disa}"))

    # Stack the split strings into a 2D array and squeeze any extra dimensions
    return np.dstack(splia).squeeze()
