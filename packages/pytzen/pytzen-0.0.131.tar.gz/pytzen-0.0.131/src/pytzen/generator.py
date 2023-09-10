import os
from pytzen.zen.docstring_composer import DocumentationGenerator
from pytzen.zen.class_generator import ClassPattern
from pytzen.zen.notebook_exporter import NotebookConverter

class ZenGenerator:
    """
    The ZenGenerator facilitates the dynamic generation of class 
    structures based on specific patterns provided via JSON. 
    It is particularly designed to work with Jupyter notebooks.

    Attributes:
    - file_name (str): The name of the Jupyter notebook currently in 
    use.
    - dict_class (dict): A dictionary containing details about the new 
    class pattern.
    - outputs (dict): Attributes (outputs) of the class derived from the 
    class pattern.
    - methods (dict): Methods of the class derived from the class 
    pattern.
    - cls (ClassPattern): A dynamically generated class structure.

    Methods:
    - find_file_name(directory='.'): Determines the name of the current 
    Jupyter notebook.
    - generate_subclass(subclass): Dynamically generates subclasses for 
    'outputs' or 'methods' based on the provided subclass parameter.
    - create_method(method_name): A decorator for linking blueprint 
    methods and runtime wrapper for method behavior validation.
    - export(path_md=None, path_py=None, conversions=None): Exports the 
    current Jupyter notebook in Markdown and Python formats.

    Note: This class leverages external classes such as 
    `DocumentationGenerator`, `ClassPattern`, and `NotebookConverter` 
    from the 'pytzen.zen' package to fulfill its functionality.
    """
    
    def __init__(self, json_path=None) -> None:

        # Check if it is running in a Jupyter Notebook for development.
        self.dev = self.is_jupyter()
        
        # Find the name of the Jupyter notebook currently in use.
        self.file_name = self.find_file_name()

        # Use the provided JSON path to extract new 
        # class pattern details.
        dict_gen = DocumentationGenerator(json_path=json_path)
        self.dict_class = dict_gen.json_obj
        
        # Store class attributes (outputs) and methods separately.
        self.outputs = self.dict_class['outputs']
        self.methods = self.dict_class['methods']
        
        # Dynamically generate the structure of the class.
        cls_gen = ClassPattern(dict_class=self.dict_class)
        self.cls = cls_gen.ClassDesign
        self.generate_inputs()
        
        # Populate the class with attribute and method blueprints.
        self.cls.out = self.generate_subclass(subclass='outputs')
        self.cls.met = self.generate_subclass(subclass='methods')

    def find_file_name(self, directory='.'):
        """
        Determines the name of the current Jupyter notebook.

        Parameters:
        - directory (str): The directory where the notebook resides. 
        Defaults to the current directory.

        Returns:
        - str: The name of the notebook without its file extension.

        Raises:
        - ValueError: If there isn't exactly one notebook in the 
        directory.
        """
        
        # Get a list of all Jupyter notebook files in the 
        # current directory.
        nb_files = [f for f in os.listdir(directory) if f.endswith('.ipynb')]

        # Expecting a single notebook, so return its name 
        # (without the file extension).
        if len(nb_files) == 1:
            return nb_files[0].split('.')[0]
        else:
            # If not exactly one, raise an error.
            raise ValueError("Please let one saved notebook in the folder.")
    
    def generate_inputs(self):
        for k in self.dict_class['inputs']:
            setattr(self, k, None)
            print(k)

    def generate_subclass(self, subclass):
        """
        Dynamically generates subclasses for either 'outputs' or 
        'methods', based on the provided subclass parameter.

        Parameters:
        - subclass (str): Type of the subclass to generate 
        ('outputs' or 'methods').

        Returns:
        - type: A dynamically generated subclass.
        """
        
        # Placeholder for collecting subclass details.
        dict_subclass = {}
        # Choose the subclass type, if ouputs or methods.
        subclass_objects = (self.methods if subclass == 'methods' 
                            else self.outputs)
        
        for name, desc in subclass_objects.items():
            # Create documentation for each subclass item.
            subclass_items = DocumentationGenerator(json_obj=desc)
            desc = subclass_items.docstring
            
            # Represent each method as a type, with its documentation.
            dict_subclass[name] = type(name, (object,), {'__doc__': desc})
            
        # Create a dynamic class 'methods' with the defined methods.
        generated_cubclass = type('subclass', (object,), dict_subclass)
        
        # Assign documentation to the subclass.
        generated_cubclass.__doc__ = """TODO: subclasses docstring"""

        return generated_cubclass

    def create_method(self, method_name):
        """
        Returns a decorator to link blueprint methods. The decorator 
        provides a runtime wrapper to validate and possibly modify the 
        method behavior based on the class's blueprint.

        Parameters:
        - method_name (str): The name of the method to link.

        Returns:
        - function: A decorator function.

        Raises:
        - AttributeError: If the given method name isn't found in the 
        methods of the class blueprint.
        """
        
        # Define the primary decorator to link blueprint methods.
        def decorator(func):
            # A runtime wrapper to validate and possibly modify 
            # method behavior.
            def wrapper(*args, **kwargs):
                # Keep track of original attributes to detect 
                # unauthorized changes later.
                backup_attributes = set(self.cls.out.__dict__.keys())
                
                # Call the original function.
                result = func(self.cls, *args, **kwargs)
                
                # Identify any unauthorized new attributes 
                # added by the function.
                added_attributes = (
                    set(self.cls.out.__dict__.keys()) - backup_attributes)
                
                # Validate the new attributes against the blueprint.
                for attr in added_attributes:
                    if attr not in self.cls.outputs:
                        cls = self.cls.__name__
                        e = f"Attribute '{attr}' is not allowed in {cls}.att"
                        delattr(self.cls.out, attr)
                        raise AttributeError(e)
    
                return result

            # Connect the wrapper to the actual method in the blueprint.
            nested_method = getattr(self.cls.met, method_name, None)
            if nested_method:
                nested_method.exec = wrapper
            else:
                cls = self.cls.__name__
                error = f"'{method_name}' not found in methods of {cls}."
                raise AttributeError(error)

            return wrapper

        return decorator
    
    def export(self, path_md=None, path_py=None, conversions=None):
        """
        Exports the current Jupyter notebook to different formats, 
        primarily Markdown and Python.

        Parameters:
        - path_md (str, optional): The path to save the exported 
        Markdown file.
        - path_py (str, optional): The path to save the exported 
        Python file.
        - conversions (list, optional): A list of desired output 
        formats. Example: ['md', 'py']

        Note:
        - If the 'py' format is specified in the conversions list, 
        the 'zen.export()' string will be removed from the 
        exported Python script.
        """
        
        # Convert the notebook to both Markdown and Python formats.
        converter = NotebookConverter(
            notebook_name=self.file_name, 
            path_md=path_md, 
            path_py=path_py,
            conversions=conversions
        )
        # Remove export function from exported python script
        if 'py' in converter.conversions:
            with open(converter.path_py, 'r') as file:
                file_contents = file.read()
                file_contents = file_contents.replace('zen.export()', '')
            with open(converter.path_py, 'w') as file:
                file.write(file_contents)


    def is_jupyter(self):
        try:
            get_ipython()
            return True
        except NameError:
            return False
