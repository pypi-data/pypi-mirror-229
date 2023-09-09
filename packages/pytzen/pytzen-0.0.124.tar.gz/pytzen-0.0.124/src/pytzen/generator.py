import os
from pytzen.zen.docstring_composer import DocumentationGenerator
from pytzen.zen.class_generator import ClassPattern
from pytzen.zen.notebook_exporter import NotebookConverter

class ZenGenerator:
    """TODO: ZenGenerator docstring"""
    
    def __init__(self, json_path=None) -> None:
        
        # Find the name of the Jupyter notebook currently in use.
        self.class_name = self.find_class_name()

        # Use the provided JSON path to extract new class pattern details.
        dict_gen = DocumentationGenerator(json_path=json_path)
        self.dict_class = dict_gen.json_obj
        
        # Store class attributes (outputs) and methods separately.
        self.outputs = self.dict_class['outputs']
        self.methods = self.dict_class['methods']
        
        # Dynamically generate the structure of the class.
        cls_gen = ClassPattern(dict_class=self.dict_class)
        self.cls = cls_gen.ClassDesign
        
        # Populate the class with attribute and method blueprints.
        self.cls.out = self.generate_subclass(subclass='outputs')
        self.cls.met = self.generate_subclass(subclass='methods')

    def find_class_name(self, directory='.'):
        
        # Get a list of all Jupyter notebook files in the current directory.
        nb_files = [f for f in os.listdir(directory) if f.endswith('.ipynb')]

        # Expecting a single notebook, so return its name (without the file extension).
        if len(nb_files) == 1:
            return nb_files[0].split('.')[0]
        else:
            # If not exactly one, raise an error.
            raise ValueError("Please save the notebook first.")

    def generate_subclass(self, subclass):
        
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
        
        # Define the primary decorator to link blueprint methods.
        def decorator(func):
            
            # A runtime wrapper to validate and possibly modify method behavior.
            def wrapper(*args, **kwargs):
                
                # Keep track of original attributes to detect unauthorized changes later.
                backup_attributes = set(self.cls.out.__dict__.keys())
                
                # Call the original function.
                result = func(self.cls, *args, **kwargs)
                
                # Identify any unauthorized new attributes added by the function.
                added_attributes = (set(self.cls.out.__dict__.keys()) - backup_attributes)
                
                # Validate the new attributes against the blueprint.
                for attr in added_attributes:
                    if attr not in self.cls.outputs:
                        e = f"Attribute '{attr}' is not allowed in {self.cls.__name__}.att"
                        delattr(self.cls.out, attr)
                        raise AttributeError(e)
    
                return result

            # Connect the wrapper to the actual method in the blueprint.
            nested_method = getattr(self.cls.met, method_name, None)
            if nested_method:
                nested_method.exec = wrapper
            else:
                error = f"'{method_name}' not found in methods of {self.cls.__name__}."
                raise AttributeError(error)

            return wrapper

        return decorator
    
    def export(self, path_md=None, path_py=None, conversions=None):
        
        # Convert the notebook to both Markdown and Python formats.
        converter = NotebookConverter(
            notebook_name=self.class_name, 
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