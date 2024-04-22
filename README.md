# StringDataDeque

Useful when building a string from data that can be converted into a string, in parts.

## Installation
https://pypi.org/project/StringDataDeque/
```bash
pip install StringDataDeque
```

## Uses

This is designed to be a drop-in replacement for when you might want to append to a string in a loop.

### Benefits
* Around 5 times faster than the naive implementation of appending to a string, such as
    ```python
    x = ""
    for x in collection:
        x+="new string"
    ```
* Provides many extra features that help simply code.

## Examples
```python
sd = StringDeque(sep="\n")
for x in collection:
    sd += x
# StringDeque is a specialization of StringDataDeque where conversion func is "str"
# this allows any datatype to be used which can convert to str
sd += 1
print(sd)
```

You can also pipe data into the StringDeque
```python
sd = StringDeque()
sd = [1,2,3,4,5] | sd
# or
sd |= [1,2,3,4,5]
```

StringDataDeque implements the "contains" method so you can search within it
```python
sd = StringDeque(["line_one","line_two"],sep="\n")
if "line_one" in sd:
    print("yes")
```

If you need more control over how data is added to the deque either use StringDataDeque or one of its subclasses.
```python
# convert_func is called when data is added, and format_func is called when data is printed.
int_sdd =StringDataDeque(data="test", convert_func=int, format_func=str,sep=" ")
int_sdd |= ["1","2","3","4","5"]
assert int_sdd[0] == 1
assert str(int_sdd) == "1 2 3 4 5"
```
