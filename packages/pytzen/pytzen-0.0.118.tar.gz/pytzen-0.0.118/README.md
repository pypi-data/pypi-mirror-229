# PYTZEN
This library is currently offered 'as-is' without any form of official support, maintenance, or warranty. Its primary purpose is to serve as a platform for experimentation and learning, and may not be suitable for production use. Users are invited to explore and experiment with the library, but please be aware that any issues encountered will not be actively addressed by the developers. Furthermore, the associated GitHub repository is private, which means direct access to the source code or issue tracking is not available. We do not take responsibility for any problems that may arise from using this library in a production setting. It is strongly recommended that users thoroughly test and evaluate the library's functionality and performance in a safe and controlled environment before considering any broader application.

# Zen Classes Generator

This module provides utilities for dynamic class generation and documentation formatting from a given dictionary.

## Table of Contents

- [Functions](#functions)
  - [generate_doc](#generate_doc)
  - [generate_new_class](#generate_new_class)
- [Classes](#classes)
  - [ZenGenerator](#zengenerator)
    - [Attributes](#attributes)
    - [Methods](#methods)
      - [get_attributes](#get_attributes)
      - [get_methods](#get_methods)
      - [create](#create)

---

## Functions

### generate_doc

```python
generate_doc(dict_doc: dict) -> str
```

Generates a formatted documentation string from a dictionary.

- **Parameters**
  - `dict_doc` (dict): Dictionary to be converted to a formatted string.
  
- **Returns**
  - `str`: A formatted representation of the dictionary suitable for documentation.

---

### generate_new_class

```python
generate_new_class(dict_class: dict) -> type
```

Dynamically generates a new class based on a dictionary.

- **Parameters**
  - `dict_class` (dict): Dictionary containing class details such as input attributes.
  
- **Returns**
  - `type`: A dynamically generated class.

---

## Classes

### ZenGenerator

```python
class ZenGenerator:
```

A utility for dynamically generating a class based on a dictionary.

#### Attributes

- `name` (str): Name of the class.
- `description` (str): Description of the class.
- `attributes` (dict): Attributes with their descriptions.
- `methods` (dict): Methods with their descriptions.
- `cls` (type): The generated class based on the provided dictionary.

#### Methods

##### `__init__`

```python
__init__(self, dict_class: dict) -> None
```

Constructor for `ZenGenerator`.

- **Parameters**
  - `dict_class` (dict): Dictionary defining the class.

---

##### get_attributes

```python
get_attributes(self) -> type
```

Generates a class with attributes and their respective documentation.

- **Returns**
  - `type`: A class named 'attributes' containing the specified attributes.

---

##### get_methods

```python
get_methods(self) -> type
```

Generates a class with methods and their respective documentation.

- **Returns**
  - `type`: A class named 'methods' containing the specified methods.

---

##### create

```python
create(self, method_name: str) -> decorator
```

Create a decorator to wrap a specific method of the class. This decorator ensures that the method does not introduce attributes that are not originally defined in the JSON representation.

- **Parameters**
  - `method_name` (str): Method name to be wrapped.

- **Returns**
  - `decorator`: A decorator to enforce the constraints on the method.

# Zen Generator Usage

A utility for dynamically generating a class based on a dictionary. The dictionary specifies the name, description, attributes, and methods for the new class.
JSON

{
    "name": "MyClass",
    "description": "Docstring explaining the class.",
    "input": {
        "some_input": "Docstring explaining the input.",
        "another_input": "Docstring explaining another input."
    },
    "attributes": {
        "some_attribute": "Docstring explaining the attribute.",
        "another_attribute": "Docstring explaining another attribute."
    },
    "methods": {
        "some_method": "Docstring explaining the method.",
        "another_method": "Docstring explaining another method."
    }
}
## Getting resources


```python
# If importing the code locally:
import sys
# Append the specified directory to the system's path so that modules 
# from there can be imported
sys.path.append('/home/pytzen/lab/pytzen/src')

import json
# Open the JSON file for reading
with open('/home/pytzen/lab/pytzen/usage/my_class.json', 'r') as json_file:
    # Load the contents of the JSON file into a Python dictionary
    dict_class = json.load(json_file)


# Import the ZenGenerator class from the specified module
from pytzen.generator import ZenGenerator
```

## Defining the new class


```python
# Create an instance of ZenGenerator using the dictionary loaded from 
# the JSON file
zen = ZenGenerator(dict_class=dict_class)

# Retrieve the dynamically generated class from the ZenGenerator 
# instance
MyClass = zen.cls
```
print(help(MyClass))


Help on class NewClass in module pytzen.generator:

class NewClass(builtins.object)
 |  NewClass(**kwargs)
 |  
 |  A dynamically generated class.
 |  
 |  Its attributes and documentation are defined based on the 
 |  provided dictionary.
 |  
 |  Methods defined here:
 |  
 |  __init__(self, **kwargs)
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  __dict__
 |      dictionary for instance variables (if defined)
 |  
 |  __weakref__
 |      list of weak references to the object (if defined)
 |  
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |  
 |  att = <class 'pytzen.generator.attributes'>
 |  
 |  met = <class 'pytzen.generator.methods'>

 
## Adding functionality


```python
print(MyClass.att.some_attribute.__doc__)
# Use the 'create' decorator method from the ZenGenerator instance to 
# add a new method named 'some_method'
@zen.create('some_method')
# The use of an underscore (_) as a function name indicates that the 
# name itself is not significant.
def _(MyClass, test):  
    print(test)
    MyClass.att.some_attribute = 137
    return 'New funcionality created.'

# Call the 'some_method' that we added to the instance, passing 'test' 
# as an argument
print(MyClass.met.some_method.exec('test'))
# Create an instance of the dynamically generated class
my_class = MyClass(some_input=3)
print(my_class.met.some_method.__doc__)
print(my_class.att.some_attribute)
```

    "Docstring explaining the attribute."
    test
    New funcionality created.
    "Docstring explaining the method."
    137


## Trying to add non designed attribute in `att`


```python
@zen.create('another_method')
def _(MyClass):
    MyClass.att.something_unexpected = 'Error'
    return 'Ok.'
```
MyClass.met.another_method.exec()

---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[5], line 1
----> 1 MyClass.met.another_method.exec()

File ~/lab/pytzen/src/pytzen/generator.py:235, in ZenGenerator.create..decorator..wrapper(*args, **kwargs)
    232     if attr not in self.cls.attributes:
    233         # Remove the attribute
    234         delattr(self.cls.att, attr)
--> 235         raise AttributeError(f"Attribute '{attr}' is not allowed to be added to {self.cls.__name__}.att")
    237 return result

AttributeError: Attribute 'something_unexpected' is not allowed to be added to MyClass.att
## Trying to add non designed method in `met`
@zen.create('forbidden_method')
def _(MyClass):
    return 'Ok.'


---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[8], line 2
      1 @zen.create('forbidden_method')
----> 2 def _(MyClass):
      3     return 'Ok.'

File ~/lab/pytzen/src/pytzen/generator.py:249, in ZenGenerator.create..decorator(func)
    247     cls = self.cls.__name__
    248     error = f"'{method_name}' not found in the methods of {cls}."
--> 249     raise AttributeError(error)
    251 return wrapper

AttributeError: 'forbidden_method' not found in the methods of MyClass.
## Trying to add non designed attribute in the root class


```python
@zen.create('another_method')
def _(MyClass):
    MyClass.something_unexpected = 'No Error'
    return 'Ok.'

print(MyClass.met.another_method.exec())
print(MyClass.something_unexpected)
```

    Ok.
    No Error

