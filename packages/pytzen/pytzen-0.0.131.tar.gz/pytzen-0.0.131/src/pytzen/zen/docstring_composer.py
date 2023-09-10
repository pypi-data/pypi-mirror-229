import json
import textwrap
import os

class DocumentationGenerator:
    """
    Generates a documentation string from a provided JSON object 
    or path.
    
    Given a JSON object or the path to a JSON file, this class converts
    the content into a formatted string representation suitable for use 
    as a docstring. If no specific JSON object or path is provided, 
    it attempts to find and load the first JSON file in the current 
    directory.
    
    Attributes:
        json_obj (dict): Python dictionary representation of the JSON 
        content.
        json_path (str): Path to the JSON file, if used.
        width (int): Width for formatting the documentation's text.
        indentation (int): Indentation level for JSON representation 
        in the docstring.
        docstring (str): Generated documentation string from the JSON 
        content.

    Methods:
        find_json_path(directory='.') -> str:
            Finds the path of a JSON file in the given directory.
        
        open_json() -> dict:
            Reads and parses the content of a JSON file into a 
            dictionary.

        generate() -> str:
            Converts the JSON content to a formatted docstring.
    """
    
    def __init__(self, json_obj=None, json_path=None, 
                 width=68, indentation=2):
        
        # If a json_obj (Python dictionary) isn't provided, 
        # it'll be loaded from the json_path later.
        self.json_obj = json_obj
        
        # Path to the JSON file from which data might be loaded.
        self.json_path = json_path
        
        # Setting the width for formatting the documentation's text.
        self.width = width
        
        # Indentation level for formatting the JSON representation.
        self.indentation = indentation
        
        # If no direct json_obj is provided, load it from a file.
        if not json_obj:
            if not json_path:
                # If no path is provided, try to find the JSON file 
                # automatically.
                self.json_path = self.find_json_path()
            
            # Read the JSON content from the provided or found path.
            self.json_obj = self.open_json()
        
        # Convert the JSON object to a formatted docstring.
        self.docstring = self.generate()

    def find_json_path(self, directory='.') -> str:
        """
        Finds the path of a JSON file in the given directory.

        Searches the specified directory for JSON files. If only one
        JSON file is found, it returns its path. Otherwise, raises 
        an error if no specific path is provided and multiple 
        JSON files are found.

        Parameters:
            directory (str, optional): Directory to search for the JSON 
            files. Defaults to the current directory.

        Returns:
            str: Path of the located JSON file.

        Raises:
            ValueError: If no specific path is provided and multiple 
                        JSON files exist in the directory.
        """
        
        # Find all JSON files in the given directory.
        json_files = [f for f in os.listdir(directory) 
                      if f.endswith('.json')]

        # If only one JSON file is found, return its path.
        if len(json_files) == 1:
            return os.path.join(directory, json_files[0])
        else:
            # Raise an error if no specific path is provided and 
            # multiple JSON files exist.
            raise ValueError(
                "Please declare a path in the class instance.")
        
    def open_json(self) -> dict:
        """
        Reads and parses the content of a JSON file into a dictionary.
    
        Uses the json_path attribute to open and read the content 
        of the corresponding JSON file. The content is then parsed 
        into a Python dictionary.
    
        Returns:
            dict: Dictionary representation of the JSON file content.
        """

        # Open and read the JSON file.
        with open(self.json_path, 'r') as json_file:
            # Parse the JSON content to a Python dictionary.
            json_obj = json.load(json_file)

        return json_obj
    
    def generate(self) -> str:
        """
        Converts the JSON content to a formatted docstring.

        Takes the loaded JSON content, either from a provided object 
        or read from a file, and converts it into a string 
        representation formatted to the specified width and indentation.
        This formatted string is intended to be suitable for use as a 
        docstring.

        Returns:
            str: Formatted string representation of the JSON content.
        """
        
        # Convert the Python dictionary (JSON object) to a string 
        # representation.
        doc = json.dumps(self.json_obj, indent=self.indentation)
        
        # Ensure each line of the docstring doesn't exceed 
        # the set width.
        doc = [textwrap.fill(line, width=self.width) 
               for line in doc.splitlines()]
        
        # Apply the format function to finalize the 
        # docstring's appearance.
        return '\n'.join(doc)
