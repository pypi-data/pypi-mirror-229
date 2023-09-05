import json
import textwrap

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
        
        Its attributes and documentation are defined based on the 
        provided dictionary.
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
    
    return NewClass
                
class ZenGenerator:
    """
    A utility for dynamically generating a class based on a dictionary.

    The dictionary specifies the name, description, attributes, and 
    methods for the new class.
    
    Attributes:
        name (str): Name of the class.
        description (str): Description of the class.
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
        self.dict_class = dict_class
        self.name = dict_class['name']
        self.description = dict_class['description']
        self.attributes = dict_class['attributes']
        self.methods = dict_class['methods']
        
        # Generate the main class
        self.cls = generate_new_class(dict_class=dict_class)
        
        # Add attributes and methods to the generated class
        self.cls.att = self.get_attributes()
        self.cls.met = self.get_methods()

    def get_attributes(self):
        """
        Generates a class with attributes and their respective 
        documentation.

        Returns:
            type: A class named 'attributes' containing the specified 
            attributes.
        """
        dict_attr = {}
        for name, desc in self.attributes.items():
            desc = generate_doc(desc)
            dict_attr[name] = type(name, (object,), {'__doc__': desc})
        return type('attributes', (object,), dict_attr)

    def get_methods(self):
        """
        Generates a class with methods and their respective 
        documentation.

        Returns:
            type: A class named 'methods' containing the specified 
            methods.
        """
        dict_meth = {}
        for name, desc in self.methods.items():
            desc = generate_doc(desc)
            dict_meth[name] = type(name, (object,), {'__doc__': desc})
        return type('methods', (object,), dict_meth)
   
    def create(self, method_name):
        """
        Create a decorator to wrap a specific method of the class.

        This decorator ensures that the method does not introduce 
        attributes that are not originally defined in the JSON 
        representation.
        
        Args:
            method_name (str): Method name to be wrapped.

        Returns:
            decorator: A decorator to enforce the constraints on the 
            method.
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
