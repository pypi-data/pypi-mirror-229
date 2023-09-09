from pytzen.zen.docstring_composer import DocumentationGenerator

class ClassPattern:
    """TODO: ClassPattern docstring"""

    def __init__(self, dict_class):
        # Store the dictionary that describes the desired class structure.
        self.dict_class = dict_class

        # Generate the class blueprint based on the given class structure.
        self.ClassDesign = self.generate_class()

    def generate_class(self):

        dict_class = self.dict_class

        # Inner class representing the dynamic blueprint of our target class.
        class ClassDesign:
            """TODO: ClassDesign docstring before instantiation"""

            def __init__(self, **kwargs):
                # Use the DocumentationGenerator to create a docstring 
                # for the class from the JSON description.
                gen_doc = DocumentationGenerator(json_obj=dict_class)
                self.__doc__ = gen_doc.docstring

                # Extract the expected inputs for the class from the class dictionary.
                class_inputs = dict_class['inputs']

                # Initialize all class attributes to None by default.
                for k, v in class_inputs.items():
                    setattr(self, k, None)

                # Override default attribute values with those provided during instantiation.
                for k, v in kwargs.items():
                    # Check if the attribute is allowed in this class.
                    if k in class_inputs:
                        setattr(self, k, v)
                    else:
                        # Raise an error if an unexpected attribute is provided.
                        error = f"Invalid attribute '{k}' for this class."
                        raise ValueError(error)
                    
                # Check if all inputs were given
                missed = set(class_inputs.keys()) - set(kwargs.keys())
                if not set(class_inputs.keys()) == set(kwargs.keys()):
                    error = f'These inputs are missed: {missed}.'
                    raise ValueError(error)

                # Dynamically attach methods to the class based on the 'methods' in the class dictionary.
                methods_defined = []
                for method_name in dict_class['methods']:
                    met_class = getattr(self.met, method_name, None)
                    if met_class and hasattr(met_class, 'exec'):
                        # Get the method implementation.
                        method = getattr(met_class, 'exec')
                        # Assign the method's documentation.
                        method.__doc__ = dict_class['methods'][method_name]
                        # Attach the method to our class.
                        setattr(self, method_name, method)
                        methods_defined.append(method_name)

                    else:
                        missed = set(dict_class['methods']) - set(methods_defined)
                        error = f'These methods are missed: {missed}.'
                        raise ValueError(error)

        return ClassDesign
