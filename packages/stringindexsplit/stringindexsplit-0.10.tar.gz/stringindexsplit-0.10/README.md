# simplifies the process of splitting a list of strings at specified character indices

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install stringindexsplit


## Description:

The SplitStringsAtIndices package is a Python utility that simplifies the process of splitting a 
list of strings at specified character indices. 
Whether you're working with text data in data analysis, natural language processing, or text processing tasks, 
this package provides a handy tool to efficiently split strings and extract substrings based on your requirements.

## Key Features:

### Flexible Input: 

Accepts a variety of input formats, including lists, tuples, and NumPy arrays, making 
it compatible with different data structures.

### Precise Splitting: 

Specify the exact character indices at which you want to split your strings, 
giving you full control over the extraction process.

### Efficient Processing: 

Utilizes NumPy for efficient array manipulation, 
ensuring fast and optimized splitting of strings.


### 2D NumPy Output: 

Returns a 2D NumPy array where each row contains the split strings, 
facilitating further analysis and manipulation.
Why Choose SplitStringsAtIndices?


```python

split_list_of_strings_at_indices(
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

```