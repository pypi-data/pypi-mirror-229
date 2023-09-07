# randomfactory

**randomfactory** is a helper function for generating random output that is used in testcase.

## Installation

```bash
$ pip install randomfactory
```

randomfactory supports Python 3.8 and newer.

## Usage

```python
from randomfactory import *

# Generate a random integer between 0 and 100
test_int = generate_integer(0, 100)
print(test_int) # 42

# Generate a random alphabet
test_alphabet = generate_alphabet()
print(test_alphabet) # 'a'

# Generate a random string with length 10
test_string = generate_string(10)
print(test_string) # 'abcdefghij'

# Generate a random string with length 10 and only contains 'a', 'b', 'c'
test_string = generate_string(10, ['a', 'b', 'c'])
print(test_string) # 'abacacabba'

# Generate a random word
test_word = generate_word(10)
print(test_word) # 'abcdefghij'

# Generate an array
test_array = generate_array(10, 0, 100)
print(test_array) # [42, 42, 32, 23, 42, 42, 13, 42, 42, 42]

# Generate 2d array
test_2d_array = generate_2d_array(3, 2, 0, 100)
print(test_2d_array) # [[12, 42], [15, 22], [42, 31]]

# Generate an array that contains only unique elements
test_unique_array = generate_unique_array(4, 0, 100)
print(test_unique_array) # [42, 32, 23, 13]

# Generate a subset of an array
test_subset = generate_subseq([1, 2, 3, 4, 5], 3)
print(test_subset) # [1, 3, 4]
```
