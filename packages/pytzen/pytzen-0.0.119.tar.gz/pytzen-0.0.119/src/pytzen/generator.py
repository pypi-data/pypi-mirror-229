import json
import textwrap

ATT_DOC = """
`att` (Attributes Blueprint)

A meta-representation of the potential attributes that the 
generated class can produce or utilize during its pipeline 
operations. Each attribute within `att` is itself a class, 
designed primarily to carry documentation about the attribute

- **Direct vs. Pipeline Attributes:** The direct attributes, 
initialized upon object instantiation, serve as inputs required 
for the class to function. In contrast, `att` embodies the 
attributes that can be utilized or produced as outputs from the 
class's methods.

- **Static Blueprint:** While `att` presents a predefined 
blueprint based on the initial dictionary provided to the 
generator, new attributes cannot be added to `att` 
post-instantiation. However, direct attributes of the generated 
class can be dynamically modified or expanded.

In essence, `att` acts as a reference map, charting the terrain 
of attributes that the class's methods are designed to interact 
with.
"""

MET_DOC = """
`met` (Methods Blueprint):

A structured repository encapsulating the potential methods that 
the generated class can employ. Each entry within `met` is 
itself a class, designed to:

1. **Hold Documentation:** Providing a detailed overview about 
the method's purpose, parameters, and expected behavior.

2. **Method Anchor:** Acting as an endpoint to reference the 
actual method implementations. These methods must be added 
before the class instantiation using decorators.

Upon incorporation using the decorator, these methods are 
anchored to `met` through the 'exec' reference, which points to 
the wrapped function (wrapper). While `met` showcases a 
predetermined list of methods based on the initial dictionary 
supplied to the generator, the actual methods need to be 
anchored prior to instantiation.

In essence, `met` serves as both a roadmap and a linkage 
mechanism, highlighting the possible methods and connecting them 
to their implementations for the generated class.
"""



def generate_doc(dict_doc):
    """
    Generate formatted documentation string from a dictionary.

    Args:
        dict_doc (dict): Dictionary to be converted to a formatted 
        string.

    Returns:
        str: A formatted representation of the dictionary suitable for 
        documentation.
    """
    doc = json.dumps(dict_doc, indent=2)
    doc = [textwrap.fill(line, width=68) for line in doc.splitlines()]
    doc = '\n'.join(doc)
    return doc


def generate_new_class(dict_class):
    """
    Dynamically generate a new class based on a dictionary.

    Args:
        dict_class (dict): Dictionary containing class details such as 
        input attributes.

    Returns:
        type: A dynamically generated class.
    """
    
    class NewClass:
        """
        A dynamically generated class.

        Before instantiation, this class offers a static description. 
        However, once instantiated with a specific dictionary, the instance 
        will carry a tailored docstring based on the provided dictionary's 
        structure and content.

        It dynamically adjusts its attributes, methods, and documentation 
        based on the provided dictionary during instantiation.
        """
    
        
        def __init__(self, **kwargs):
            self.__doc__ = generate_doc(dict_doc=dict_class)
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
    
    return NewClass

                
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
    
    def __init__(self, dict_class: dict) -> None:
        """
        Constructor for ZenGenerator.
        
        Args:
            dict_class (dict): Dictionary defining the class.
        """
        
        self.attributes = dict_class['attributes']
        self.methods = dict_class['methods']
        
        # Generate the main class
        self.cls = generate_new_class(dict_class=dict_class)
        
        # Add attributes and methods to the generated class
        self.cls.att = self.get_attributes()
        self.cls.met = self.get_methods()

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
        att.__doc__ = ATT_DOC
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
        met.__doc__ = MET_DOC
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
