import json
import textwrap
import os

class DocumentationGenerator:
    """TODO: DocumentationGenerator docstring"""
    
    def __init__(self, json_obj=None, json_path=None, width=68, indentation=2):
        
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
                # If no path is provided, try to find the JSON file automatically.
                self.json_path = self.find_json_path()
            
            # Read the JSON content from the provided or found path.
            self.json_obj = self.open_json()
        
        # Convert the JSON object to a formatted docstring.
        self.docstring = self.generate()

    def find_json_path(self, directory='.') -> str:
        
        # Find all JSON files in the given directory.
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

        # If only one JSON file is found, return its path.
        if len(json_files) == 1:
            return os.path.join(directory, json_files[0])
        else:
            # Raise an error if no specific path is provided and multiple JSON files exist.
            raise ValueError("Please declare a path in the class instance.")
        
    def open_json(self) -> dict:

        # Open and read the JSON file.
        with open(self.json_path, 'r') as json_file:
            # Parse the JSON content to a Python dictionary.
            json_obj = json.load(json_file)

        return json_obj
    
    def generate(self) -> str:
        
        # Convert the Python dictionary (JSON object) to a string representation.
        doc = json.dumps(self.json_obj, indent=self.indentation)
        
        # Ensure each line of the docstring doesn't exceed the set width.
        doc = [textwrap.fill(line, width=self.width) for line in doc.splitlines()]
        
        # Apply the format function to finalize the docstring's appearance.
        return '\n'.join(doc)
