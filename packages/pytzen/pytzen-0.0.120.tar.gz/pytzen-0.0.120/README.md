# PYTZEN

This library is currently offered 'as-is' without any form of official support, maintenance, or warranty. Its primary purpose is to serve as a platform for experimentation and learning, and may not be suitable for production use. Users are invited to explore and experiment with the library, but please be aware that any issues encountered will not be actively addressed by the developers. Furthermore, the associated GitHub repository is private, which means direct access to the source code or issue tracking is not available. We do not take responsibility for any problems that may arise from using this library in a production setting. It is strongly recommended that users thoroughly test and evaluate the library's functionality and performance in a safe and controlled environment before considering any broader application.

# Zen Generator Classes Design Pattern


```python
DEV = True # boolean
import json
import textwrap
import json
import os
```


```python
ATT = [
    "`att` (Attributes Blueprint)",
    "A meta-representation of the potential attributes that the generated class can produce or utilize during its pipeline operations. Each attribute within `att` is itself a class, designed primarily to carry documentation about the attribute.",
    "- **Direct vs. Pipeline Attributes:** The direct attributes, initialized upon object instantiation, serve as inputs required for the class to function. In contrast, `att` embodies the attributes that can be utilized or produced as outputs from the class's methods.",
    "- **Static Blueprint:** While `att` presents a predefined blueprint based on the initial dictionary provided to the generator, new attributes cannot be added to `att` post-instantiation. However, direct attributes of the generated class can be dynamically modified or expanded.",
    "In essence, `att` acts as a reference map, charting the terrain of attributes that the class's methods are designed to interact with."
    ]

MET = [
    "`met` (Methods Blueprint):",
    "A structured repository encapsulating the potential methods that the generated class can employ. Each entry within `met` is itself a class, designed to:",
    "1. **Hold Documentation:** Providing a detailed overview about the method's purpose, parameters, and expected behavior.",
    "2. **Method Anchor:** Acting as an endpoint to reference the actual method implementations. These methods must be added before the class instantiation using decorators.",
    "Upon incorporation using the decorator, these methods are anchored to `met` through the 'exec' reference, which points to the wrapped function (wrapper). While `met` showcases a predetermined list of methods based on the initial dictionary supplied to the generator, the actual methods need to be anchored prior to instantiation.",
    "In essence, `met` serves as both a roadmap and a linkage mechanism, highlighting the possible methods and connecting them to their implementations for the generated class."
    ]
```


```python
def generate_doc(json_obj):
    """
    Generate formatted documentation string from a dictionary.

    Args:
        json_obje (dict): JSON object to be converted to a formatted 
        string.

    Returns:
        str: A formatted representation of the dictionary suitable for 
        documentation.
    """
    doc = json.dumps(json_obj, indent=2)
    doc = [textwrap.fill(line, width=68) for line in doc.splitlines()]
    doc = '\n'.join(doc)
    for char in ['{', '}', '[', ']', '"']:
        doc = doc.replace(char, '')
    doc = doc.replace(',\n', '\n')
    return doc
```


```python
def class_pattern(dict_class):
    """
    Dynamically generate a new class based on a dictionary.

    Args:
        dict_class (dict): Dictionary containing class details such as 
        input attributes.

    Returns:
        type: A dynamically generated class.
    """
    
    class ClassDesign:
        """
        A dynamically generated class.

        Before instantiation, this class offers a static description. 
        However, once instantiated with a specific dictionary, the 
        instance will carry a tailored docstring based on the provided 
        dictionary's structure and content.

        It dynamically adjusts its attributes, methods, and 
        documentation based on the provided dictionary during 
        instantiation.
        """
    
        def __init__(self, **kwargs):
            self.__doc__ = generate_doc(json_obj=dict_class)
            class_input = dict_class['input']

            # Initializing attributes
            for k, v in class_input.items():
                setattr(self, k, None)

            # Overriding attributes with provided kwargs if valid
            for k, v in kwargs.items():
                if k in class_input:
                    setattr(self, k, v)
                else:
                    error = f"Invalid attribute '{k}' for this class."
                    raise ValueError(error)
            
            for method_name in dict_class['methods']:
                met_class = getattr(self.met, method_name, None)
                if met_class and hasattr(met_class, 'exec'):
                    method = getattr(met_class, 'exec')
                    method.__doc__ = dict_class['methods'][method_name]
                    setattr(self, method_name, method)
    
    return ClassDesign
```


```python
class ZenGenerator:
    """
    A utility for dynamically generating a class based on a dictionary.

    The dictionary specifies the name, description, input values, 
    attributes, and methods for the new class.
    
    Attributes:
        attributes (dict): Attributes with their descriptions.
        methods (dict): Methods with their descriptions.
        cls (type): The generated class based on the provided 
        dictionary.
    """
    
    def __init__(self, path_json: str) -> None:
        """
        Constructor for ZenGenerator.
        
        Args:
            dict_class (dict): Dictionary defining the class.
        """
        self.path = path_json
        dict_class = self.open_json()
        self.attributes = dict_class['attributes']
        self.methods = dict_class['methods']
        
        # Generate the main class
        self.cls = class_pattern(dict_class=dict_class)
        
        # Add attributes and methods to the generated class
        self.cls.att = self.get_attributes()
        self.cls.met = self.get_methods()

    def open_json(self):

        # Open the JSON file for reading
        with open(self.path, 'r') as json_file:
            # Load the contents of the JSON file into a Python dictionary
            dict_class = json.load(json_file)
        return dict_class

    def get_attributes(self):
        """
        Generates a class with attributes blueprint and their respective 
        documentation.

        Returns:
            type: A class named 'attributes' containing the specified 
            attributes.
        """
        dict_attr = {}
        for name, desc in self.attributes.items():
            desc = generate_doc(desc)
            dict_attr[name] = type(name, (object,), {'__doc__': desc})
        att = type('attributes', (object,), dict_attr)
        att.__doc__ = generate_doc(ATT)
        return att

    def get_methods(self):
        """
        Generates a class with methods blueprint and their respective 
        documentation.

        Returns:
            type: A class named 'methods' containing the specified 
            methods.
        """
        dict_meth = {}
        for name, desc in self.methods.items():
            desc = generate_doc(desc)
            dict_meth[name] = type(name, (object,), {'__doc__': desc})
        met = type('methods', (object,), dict_meth)
        met.__doc__ = generate_doc(MET)
        return met
   
    def create(self, method_name):
        """
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
        """


        def decorator(func):
            """
            The core decorator that wraps a given function.

            Args:
                func (callable): The target function.

            Returns:
                callable: A wrapped version of the function.
            """

            def wrapper(*args, **kwargs):
                """
                Wrapper function to enforce constraints during method 
                execution.

                Args:
                    *args: Positional arguments.
                    **kwargs: Keyword arguments.

                Returns:
                    Result of the original function after applying 
                    constraints.
                """
                backup_attributes = set(self.cls.att.__dict__.keys())
                result = func(self.cls, *args, **kwargs)
                added_attributes = (set(self.cls.att.__dict__.keys())
                                    - backup_attributes)

                for attr in added_attributes:
                    if attr not in self.cls.attributes:
                        error = \
                            f"Attribute '{attr}' is not allowed" \
                            f" in {self.cls.__name__}.att"
                        delattr(self.cls.att, attr)
                        raise AttributeError(error)

                return result

            nested_method = getattr(self.cls.met, method_name, None)
            if nested_method:
                nested_method.exec = wrapper
            else:
                error = \
                    f"'{method_name}' not found in" \
                    f" methods of {self.cls.__name__}."
                raise AttributeError(error)

            return wrapper

        return decorator

    def convert_notebook(
        self, name_notebook, path_doc, name_doc_simple):
        """
        Converts a Jupyter notebook to both markdown and python script 
        formats.

        Parameters:
        - name_notebook (str): Name of the Jupyter notebook.
        - path_doc (str): Directory path where the markdown file should 
        be saved.
        - name_doc_simple (str): Desired base name for the exported 
        markdown file. The function will automatically append ".md" to 
        this base name to produce the final markdown filename. For 
        example, providing 'README' will result in an exported file 
        named 'README.md'.

        Note: Ensure the provided directory paths exist to avoid any 
        issues during file export.
        """

        name_doc = f"{name_doc_simple}.md"
        path_script = './'

        # Export to markdown
        os.system(
            (f"jupyter nbconvert --to markdown {name_notebook} "
            + f"--output-dir={path_doc} --output={name_doc}")
            )

        # Export to python script
        os.system(
            (f"jupyter nbconvert --to script {name_notebook} "
            + f"--output-dir={path_script}")
            )

```

# Usage


```python
if DEV:
    PATH_JSON = 'my_class.json'
    def doc_print(raw_content):
        print('```')
        print(raw_content)
        print('```')
    
    def help_print(content):
        print('```')
        print(help(content))
        print('```')
```

## `JSON` structure
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
## Defining the new class


```python
if DEV:
    # Create an instance of ZenGenerator using the dictionary loaded from 
    # the JSON file
    zen = ZenGenerator(path_json=PATH_JSON)

    # Retrieve the dynamically generated class from the ZenGenerator 
    # instance
    MyClass = zen.cls

    doc_print(zen)
    doc_print(MyClass)
```

    ```
    <__main__.ZenGenerator object at 0x7ff596ecac50>
    ```
    ```
    <class '__main__.class_pattern.<locals>.ClassDesign'>
    ```


## `help` before instantiation


```python
if DEV:
    help_print(MyClass)
```

    ```
    Help on class ClassDesign in module __main__:
    
    class ClassDesign(builtins.object)
     |  ClassDesign(**kwargs)
     |  
     |  A dynamically generated class.
     |  
     |  Before instantiation, this class offers a static description. 
     |  However, once instantiated with a specific dictionary, the 
     |  instance will carry a tailored docstring based on the provided 
     |  dictionary's structure and content.
     |  
     |  It dynamically adjusts its attributes, methods, and 
     |  documentation based on the provided dictionary during 
     |  instantiation.
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
     |  att = <class '__main__.attributes'>
     |        `att` (Attributes Blueprint)
     |        A meta-representation of the potential attributes that the
     |      generated class can produce or utilize during its pipeline
     |      operations. Each attribute within `att` is itself a class, designed
     |      primarily to carry documentation about the attribute.
     |        - **Direct vs. Pipeline Attributes:** The direct attributes
     |      initialized upon object instantiation, serve as inputs required for
     |      the class to function. In contrast, `att` embodies the attributes
     |      that can be utilized or produced as outputs from the class's
     |      methods.
     |        - **Static Blueprint:** While `att` presents a predefined
     |      blueprint based on the initial dictionary provided to the generator
     |      new attributes cannot be added to `att` post-instantiation. However
     |      direct attributes of the generated class can be dynamically modified
     |      or expanded.
     |        In essence, `att` acts as a reference map, charting the terrain
     |      of attributes that the class's methods are designed to interact
     |      with.
     |  
     |  
     |  met = <class '__main__.methods'>
     |        `met` (Methods Blueprint):
     |        A structured repository encapsulating the potential methods that
     |      the generated class can employ. Each entry within `met` is itself a
     |      class, designed to:
     |        1. **Hold Documentation:** Providing a detailed overview about
     |      the method's purpose, parameters, and expected behavior.
     |        2. **Method Anchor:** Acting as an endpoint to reference the
     |      actual method implementations. These methods must be added before
     |      the class instantiation using decorators.
     |        Upon incorporation using the decorator, these methods are
     |      anchored to `met` through the 'exec' reference, which points to the
     |      wrapped function (wrapper). While `met` showcases a predetermined
     |      list of methods based on the initial dictionary supplied to the
     |      generator, the actual methods need to be anchored prior to
     |      instantiation.
     |        In essence, `met` serves as both a roadmap and a linkage
     |      mechanism, highlighting the possible methods and connecting them to
     |      their implementations for the generated class.
    
    None
    ```



```python
if DEV:
    doc_print(MyClass.att.some_attribute.__doc__)
    doc_print(MyClass.att.another_attribute.__doc__)
    doc_print(MyClass.met.some_method.__doc__)
    doc_print(MyClass.met.another_method.__doc__)
```

    ```
    Docstring explaining the attribute.
    ```
    ```
    Docstring explaining another attribute.
    ```
    ```
    Docstring explaining the method.
    ```
    ```
    Docstring explaining another method.
    ```


## Adding functionality before instantiation


```python
if DEV:
    doc_print(zen.create.__doc__)
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
if DEV:
    # Use the 'create' decorator method from the ZenGenerator instance 
    # to add a new method named 'some_method'.
    # The use of an underscore (_) as a function name indicates that the 
    # name itself is not significant.
    @zen.create('some_method')
    def _(MyClass, test):  
        print(test)
        MyClass.att.some_attribute = 137
        return 'I am printing from the new assigned funcionality.'

    # Call the 'some_method' that we added to the instance, passing 
    # 'test' as an argument.
    doc_print(MyClass.met.some_method.exec(
        'Test from method blueprint with exec().'))
    doc_print(f'My assigned attribute is {MyClass.att.some_attribute}.')
```

    Test from method blueprint with exec().
    ```
    I am printing from the new assigned funcionality.
    ```
    ```
    My assigned attribute is 137.
    ```


## Trying to add non designed attribute in `att`


```python
if DEV:
    @zen.create('another_method')
    def _(MyClass):
        MyClass.att.something_unexpected = 'Error'
        return 'Ok.'
    
    try:
        MyClass.met.another_method.exec()
    except Exception as err:
        doc_print(err)
```

    ```
    type object 'ClassDesign' has no attribute 'attributes'
    ```


## Trying to add non designed method in `met`


```python
if DEV:
    try:
        @zen.create('forbidden_method')
        def _(MyClass):
            return 'Ok.'
    except Exception as err:
        doc_print(err)
```

    ```
    'forbidden_method' not found in methods of ClassDesign.
    ```


## Trying to add non designed attribute in the root class


```python
if DEV:
    @zen.create('another_method')
    def _(MyClass):
        MyClass.something_unexpected = 'No Error'
        return 'Ok.'

    doc_print(MyClass.met.another_method.exec())
    doc_print(MyClass.something_unexpected)
```

    ```
    Ok.
    ```
    ```
    No Error
    ```


## Instance of the new class


```python
if DEV:
    # Create an instance of the dynamically generated class
    my_class = MyClass(some_input=3)
    doc_print(my_class.some_method('Testing method directly from instance.'))
    doc_print(my_class.some_method.__doc__)
```

    Testing method directly from instance.
    ```
    I am printing from the new assigned funcionality.
    ```
    ```
    Docstring explaining the method.
    ```


## `help` after instantiation


```python
if DEV:
    help_print(MyClass)
```

    ```
    Help on class ClassDesign in module __main__:
    
    class ClassDesign(builtins.object)
     |  ClassDesign(**kwargs)
     |  
     |  A dynamically generated class.
     |  
     |  Before instantiation, this class offers a static description. 
     |  However, once instantiated with a specific dictionary, the 
     |  instance will carry a tailored docstring based on the provided 
     |  dictionary's structure and content.
     |  
     |  It dynamically adjusts its attributes, methods, and 
     |  documentation based on the provided dictionary during 
     |  instantiation.
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
     |  att = <class '__main__.attributes'>
     |        `att` (Attributes Blueprint)
     |        A meta-representation of the potential attributes that the
     |      generated class can produce or utilize during its pipeline
     |      operations. Each attribute within `att` is itself a class, designed
     |      primarily to carry documentation about the attribute.
     |        - **Direct vs. Pipeline Attributes:** The direct attributes
     |      initialized upon object instantiation, serve as inputs required for
     |      the class to function. In contrast, `att` embodies the attributes
     |      that can be utilized or produced as outputs from the class's
     |      methods.
     |        - **Static Blueprint:** While `att` presents a predefined
     |      blueprint based on the initial dictionary provided to the generator
     |      new attributes cannot be added to `att` post-instantiation. However
     |      direct attributes of the generated class can be dynamically modified
     |      or expanded.
     |        In essence, `att` acts as a reference map, charting the terrain
     |      of attributes that the class's methods are designed to interact
     |      with.
     |  
     |  
     |  met = <class '__main__.methods'>
     |        `met` (Methods Blueprint):
     |        A structured repository encapsulating the potential methods that
     |      the generated class can employ. Each entry within `met` is itself a
     |      class, designed to:
     |        1. **Hold Documentation:** Providing a detailed overview about
     |      the method's purpose, parameters, and expected behavior.
     |        2. **Method Anchor:** Acting as an endpoint to reference the
     |      actual method implementations. These methods must be added before
     |      the class instantiation using decorators.
     |        Upon incorporation using the decorator, these methods are
     |      anchored to `met` through the 'exec' reference, which points to the
     |      wrapped function (wrapper). While `met` showcases a predetermined
     |      list of methods based on the initial dictionary supplied to the
     |      generator, the actual methods need to be anchored prior to
     |      instantiation.
     |        In essence, `met` serves as both a roadmap and a linkage
     |      mechanism, highlighting the possible methods and connecting them to
     |      their implementations for the generated class.
     |  
     |  
     |  something_unexpected = 'No Error'
    
    None
    ```



```python
if DEV:
    name_notebook = "generator.ipynb"
    path_doc = '/home/pytzen/lab/pytzen/'
    name_doc_simple = 'README'
    zen.convert_notebook(name_notebook, path_doc, name_doc_simple)
```

    [NbConvertApp] Converting notebook generator.ipynb to markdown
    [NbConvertApp] Writing 26232 bytes to /home/pytzen/lab/pytzen/README.md
    [NbConvertApp] Converting notebook generator.ipynb to script
    [NbConvertApp] Writing 16076 bytes to generator.py

