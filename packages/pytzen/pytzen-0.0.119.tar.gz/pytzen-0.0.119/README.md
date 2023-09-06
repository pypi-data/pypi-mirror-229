# PYTZEN
This library is currently offered 'as-is' without any form of official support, maintenance, or warranty. Its primary purpose is to serve as a platform for experimentation and learning, and may not be suitable for production use. Users are invited to explore and experiment with the library, but please be aware that any issues encountered will not be actively addressed by the developers. Furthermore, the associated GitHub repository is private, which means direct access to the source code or issue tracking is not available. We do not take responsibility for any problems that may arise from using this library in a production setting. It is strongly recommended that users thoroughly test and evaluate the library's functionality and performance in a safe and controlled environment before considering any broader application.

# ZenGenerator Documentation

The `ZenGenerator` is a utility designed for dynamically generating classes based on dictionary specifications. Its strength lies in its capacity to structure and detail attributes and methods, ensuring that the resulting class adheres strictly to the design.

---

## Main Components

### 1. `att` (Attributes Blueprint)

A meta-representation of the potential attributes that the generated class can produce or utilize during its pipeline operations. 

- **Purpose**: Each attribute within `att` is a class, primarily crafted to offer insights and documentation about the attribute itself.

#### Key Takeaways:
- **Direct vs. Pipeline Attributes**: The direct attributes, initialized upon object creation, serve as mandatory inputs for the class to function properly. Meanwhile, `att` represents the attributes that can either be used or produced as outputs from the class's methods.
  
- **Static Blueprint**: `att` represents a predefined blueprint based on the initial dictionary supplied to the generator. Once the class is instantiated, new attributes can't be added to `att`. However, you can still dynamically modify or expand direct attributes of the generated class.

### 2. `met` (Methods Blueprint)

This component is a structured database of the potential methods the generated class can implement.

- **Purpose**: Each method within `met` is a class, crafted to:
    1. **Hold Documentation**: It offers an extensive overview of the method's purpose, parameters, and expected outcomes.
    2. **Method Anchor**: Functions as a reference to link actual method implementations. These methods must be coupled before class instantiation using decorators.

#### Key Takeaways:
- **Method Linkage**: Once incorporated using the decorator, these methods are tethered to `met` via the 'exec' reference, which directs to the wrapped function (wrapper).
  
- **Dynamic Extension**: `met` displays a predefined list of methods based on the generator's initial dictionary. However, you need to link the actual methods to it before instantiation.

---

## Core Functions

### 1. `generate_doc`

This function transmutes a dictionary into a neatly formatted documentation string.

- **Parameters**:
    - `dict_doc` (dict): The dictionary to be formatted.
  
- **Returns**: A string which is a neatly structured representation of the dictionary, suitable for documentation.

### 2. `generate_new_class`

This function dynamically crafts a new class based on a dictionary's blueprint.

- **Parameters**:
    - `dict_class` (dict): Dictionary detailing class elements such as input attributes.
  
- **Returns**: A freshly minted class tailored according to the dictionary specifications.

---

## ZenGenerator Class

A hub for crafting a class dynamically based on a dictionary's blueprint. This dictionary describes the class's name, attributes, methods, and more.

### Attributes:
- `attributes` (dict): Contains attribute descriptions.
- `methods` (dict): Holds method descriptions.
- `cls` (type): The generated class according to the provided dictionary.

### Methods:

#### 1. `__init__`

Constructor for `ZenGenerator`.

- **Parameters**:
    - `dict_class` (dict): Dictionary detailing the class.

#### 2. `get_attributes`

Constructs a class encompassing the attributes blueprint and their corresponding documentation.

- **Returns**: A class termed 'attributes' incorporating the given attributes.

#### 3. `get_methods`

Builds a class detailing the methods blueprint and their accompanying documentation.

- **Returns**: A class termed 'methods' encapsulating the specified methods.

#### 4. `create`

A decorator mechanism designed to anchor a specific method to the class's `met` blueprint. It's vital to apply this decorator to couple methods to the class before instantiation.

- **Parameters**:
    - `method_name` (str): The method's name specified in the original dictionary. This name must match one of the planned methods.

- **Returns**: A decorator ensuring method constraints and integrating it with the crafted class.

---

This markdown documentation provides an overview of the `ZenGenerator` system, breaking down its components and functionalities. It ensures that any developer can understand the purpose, usage, and intricacies of the utility.

# Zen Generator Usage

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
print(ZenGenerator)
```
```
    <class 'pytzen.generator.ZenGenerator'>
```

## `JSON` structure
```
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
```
## Defining the new class


```python
# Create an instance of ZenGenerator using the dictionary loaded from 
# the JSON file
zen = ZenGenerator(dict_class=dict_class)

# Retrieve the dynamically generated class from the ZenGenerator 
# instance
MyClass = zen.cls

print(zen, MyClass, sep='\n')
```
```
    <pytzen.generator.ZenGenerator object at 0x7ff218d585e0>
    <class 'pytzen.generator.generate_new_class.<locals>.NewClass'>
```

## `help` before instantiation


```python
print(help(MyClass))
```
```
    Help on class NewClass in module pytzen.generator:
    
    class NewClass(builtins.object)
     |  NewClass(**kwargs)
     |  
     |  A dynamically generated class.
     |  
     |  Before instantiation, this class offers a static description. 
     |  However, once instantiated with a specific dictionary, the instance 
     |  will carry a tailored docstring based on the provided dictionary's 
     |  structure and content.
     |  
     |  It dynamically adjusts its attributes, methods, and documentation 
     |  based on the provided dictionary during instantiation.
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
     |      `att` (Attributes Blueprint)
     |      
     |      A meta-representation of the potential attributes that the 
     |      generated class can produce or utilize during its pipeline 
     |      operations. Each attribute within `att` is itself a class, 
     |      designed primarily to carry documentation about the attribute
     |      
     |      - **Direct vs. Pipeline Attributes:** The direct attributes, 
     |      initialized upon object instantiation, serve as inputs required 
     |      for the class to function. In contrast, `att` embodies the 
     |      attributes that can be utilized or produced as outputs from the 
     |      class's methods.
     |      
     |      - **Static Blueprint:** While `att` presents a predefined 
     |      blueprint based on the initial dictionary provided to the 
     |      generator, new attributes cannot be added to `att` 
     |      post-instantiation. However, direct attributes of the generated 
     |      class can be dynamically modified or expanded.
     |      
     |      In essence, `att` acts as a reference map, charting the terrain 
     |      of attributes that the class's methods are designed to interact 
     |      with.
     |  
     |  
     |  met = <class 'pytzen.generator.methods'>
     |      `met` (Methods Blueprint):
     |      
     |      A structured repository encapsulating the potential methods that 
     |      the generated class can employ. Each entry within `met` is 
     |      itself a class, designed to:
     |      
     |      1. **Hold Documentation:** Providing a detailed overview about 
     |      the method's purpose, parameters, and expected behavior.
     |      
     |      2. **Method Anchor:** Acting as an endpoint to reference the 
     |      actual method implementations. These methods must be added 
     |      before the class instantiation using decorators.
     |      
     |      Upon incorporation using the decorator, these methods are 
     |      anchored to `met` through the 'exec' reference, which points to 
     |      the wrapped function (wrapper). While `met` showcases a 
     |      predetermined list of methods based on the initial dictionary 
     |      supplied to the generator, the actual methods need to be 
     |      anchored prior to instantiation.
     |      
     |      In essence, `met` serves as both a roadmap and a linkage 
     |      mechanism, highlighting the possible methods and connecting them 
     |      to their implementations for the generated class.
```


```python
print(MyClass.att.some_attribute.__doc__)
print(MyClass.att.another_attribute.__doc__)
print(MyClass.met.some_method.__doc__)
print(MyClass.met.another_method.__doc__)
```
```
    "Docstring explaining the attribute."
    "Docstring explaining another attribute."
    "Docstring explaining the method."
    "Docstring explaining another method."
```

## Adding functionality before instantiation


```python
print(zen.create.__doc__)
```

```    
            Create a decorator to anchor a specific method to the class's 
            `met` blueprint.
    
            This decorator serves dual purposes:
    
            1. **Method Linkage:** It attaches the method to its 
            corresponding entry within the `met` blueprint using the 'exec' 
            reference, which points to the wrapped function. This allows the 
            generated class to be aware of and utilize the method during 
            runtime.
    
            2. **Attribute Safety:** The decorator ensures that the method 
            does not introduce new attributes to `att`, preserving its 
            predefined structure. This ensures that only designed 
            attributes, specified during the initial class generation, are 
            used.
    
            Only methods that have been predefined in the initial dictionary 
            (thus present in the `met` blueprint) can be anchored using this 
            decorator. Any attempt to anchor a non-designed method will 
            result in an error.
    
            It's essential to use this decorator to bind methods to the 
            class before instantiation to preserve the integrity of the 
            class's design.
    
            Args:
                method_name (str): The method name specified in the initial 
                dictionary, which corresponds to an entry within the `met` 
                blueprint. This name must be one of the designed methods.
    
            Returns:
                decorator: A decorator to enforce the constraints on the 
                method and link it to the generated class.
```            



```python
# Use the 'create' decorator method from the ZenGenerator instance to 
# add a new method named 'some_method'
@zen.create('some_method')
# The use of an underscore (_) as a function name indicates that the 
# name itself is not significant.
def _(MyClass, test):  
    print(test)
    MyClass.att.some_attribute = 137
    return 'I am printing from the new assigned funcionality.'

# Call the 'some_method' that we added to the instance, passing 'test' 
# as an argument
print(MyClass.met.some_method.exec('Test from method blueprint with exec().'))
print(f'My assigned attribute is {MyClass.att.some_attribute}.')
```
```
    Test from method blueprint with exec().
    I am printing from the new assigned funcionality.
    My assigned attribute is 137.
```

## Trying to add non designed attribute in `att`


```python
@zen.create('another_method')
def _(MyClass):
    MyClass.att.something_unexpected = 'Error'
    return 'Ok.'

MyClass.met.another_method.exec()
```

```
    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    Cell In[7], line 6
          3     MyClass.att.something_unexpected = 'Error'
          4     return 'Ok.'
    ----> 6 MyClass.met.another_method.exec()


    File ~/lab/pytzen/src/pytzen/generator.py:262, in ZenGenerator.create.<locals>.decorator.<locals>.wrapper(*args, **kwargs)
        258 added_attributes = (set(self.cls.att.__dict__.keys())
        259                     - backup_attributes)
        261 for attr in added_attributes:
    --> 262     if attr not in self.cls.attributes:
        263         error = \
        264             f"Attribute '{attr}' is not allowed" \
        265             f" in {self.cls.__name__}.att"
        266         delattr(self.cls.att, attr)


    AttributeError: type object 'NewClass' has no attribute 'attributes'
```

## Trying to add non designed method in `met`


```python
@zen.create('forbidden_method')
def _(MyClass):
    return 'Ok.'
```

```
    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    Cell In[15], line 2
          1 @zen.create('forbidden_method')
    ----> 2 def _(MyClass):
          3     return 'Ok.'


    File ~/lab/pytzen/src/pytzen/generator.py:276, in ZenGenerator.create.<locals>.decorator(func)
        272 else:
        273     error = \
        274         f"'{method_name}' not found in" \
        275         f" methods of {self.cls.__name__}."
    --> 276     raise AttributeError(error)
        278 return wrapper


    AttributeError: 'forbidden_method' not found in methods of NewClass.
```

## Trying to add non designed attribute in the root class


```python
@zen.create('another_method')
def _(MyClass):
    MyClass.something_unexpected = 'No Error'
    return 'Ok.'

print(MyClass.met.another_method.exec())
print(MyClass.something_unexpected)
```
```
    Ok.
    No Error
```

## Instance of the new class


```python
# Create an instance of the dynamically generated class
my_class = MyClass(some_input=3)
print(my_class.some_method('Testing method directly from instance.'))
print(my_class.some_method.__doc__)
```
```
    Testing method directly from instance.
    I am printing from the new assigned funcionality.
    Docstring explaining the method.
```

## `help` after instantiation


```python
print(help(my_class))
```
```
    Help on NewClass in module pytzen.generator:
    
    <pytzen.generator.generate_new_class.<locals>.NewClass object>
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
```