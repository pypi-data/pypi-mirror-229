from pytzen.zen.docstring_composer import DocumentationGenerator

class ClassPattern:
    """
    A class responsible for dynamically generating a blueprint of 
    a target class.

    The `ClassPattern` takes a dictionary representation of a class's 
    desired structure, including its inputs (attributes) and methods. 
    It then produces a dynamic blueprint of the target class, which 
    can be used to validate and instantiate the target class based 
    on this pattern.

    Attributes:
    - dict_class (dict): The dictionary describing the desired structure 
    of the target class.
    - ClassDesign (type): A dynamically generated class serving as the 
    blueprint for the target class.

    Note:
    The dynamic blueprint class (i.e., `ClassDesign`) expects all 
    attributes mentioned in 'inputs' to be provided during 
    instantiation. Additionally, it dynamically binds methods 
    defined in the 'methods' section of the `dict_class` to the 
    instance, allowing them to be invoked as regular methods.
    """

    def __init__(self, dict_class):
        # Store the dictionary that describes the desired 
        # class structure.
        self.dict_class = dict_class

        # Generate the class blueprint based on the given 
        # class structure.
        self.ClassDesign = self.generate_class()

    def generate_class(self):
        """
        Dynamically generates the blueprint of the target class based on 
        the provided class structure.

        The method creates an inner class `ClassDesign` that represents 
        the blueprint of the target class. 
        This inner class expects all attributes mentioned in the 
        'inputs' section of the `dict_class` to be provided during 
        instantiation. It also dynamically binds methods defined in 
        the 'methods' section of the `dict_class` to the instance.

        Returns:
        - type: The dynamically generated `ClassDesign` class.
        """

        dict_class = self.dict_class

        # Inner class representing the dynamic blueprint of our 
        # target class.
        class ClassDesign:
            """
            Dynamic blueprint representing the target class structure.

            This class serves as a blueprint for the desired class 
            structure defined in `dict_class`.
            It initializes attributes based on the 'inputs' section of 
            the `dict_class` and expects all of them to be provided 
            during instantiation. Moreover, it dynamically binds methods 
            defined in the 'methods' section of the `dict_class` to the 
            instance.

            Attributes:
                - Based on the 'inputs' section of `dict_class`.

            Methods:
                - Dynamically bound based on the 'methods' section of 
                `dict_class`.
            """

            def __init__(self, **kwargs):
                # Use the DocumentationGenerator to create a docstring 
                # for the class from the JSON description.
                gen_doc = DocumentationGenerator(json_obj=dict_class)
                self.__doc__ = gen_doc.docstring

                # Override default attribute values with those provided 
                # during instantiation.
                given_inputs = []
                for k, v in kwargs.items():
                    # Check if the attribute is allowed in this class.
                    if k in dict_class['inputs']:
                        setattr(self, k, v)
                        given_inputs.append(k)
                    else:
                        # Raise an error if an unexpected attribute 
                        # is provided.
                        error = f"Invalid attribute '{k}' for this class."
                        raise ValueError(error)
                
                # Info about missing inputs
                missed = (set(dict_class['inputs']) - set(given_inputs))
                if missed:
                    print(f'These inputs are missed: {missed}.')

                # Dynamically attach methods to the class based on the 
                # 'methods' in the class dictionary.
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

                # Info about missing methods
                missed = (set(dict_class['methods']) - set(methods_defined))
                if missed:
                    print(f'These methods are missed: {missed}.')

        return ClassDesign
