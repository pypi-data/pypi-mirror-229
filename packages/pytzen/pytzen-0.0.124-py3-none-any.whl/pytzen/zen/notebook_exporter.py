import os
import nbformat
from nbconvert import PythonExporter, MarkdownExporter

class NotebookConverter:
    """TODO: NotebookConverter docstring"""

    def __init__(self, conversions=['md', 'py'], notebook_name=None, path_md=None, path_py=None):
        
        # If the provided notebook_name doesn't have a '.ipynb' extension, add it.
        if not notebook_name.endswith('.ipynb'):
            notebook_name += '.ipynb'
        
        # Check if the notebook exists in the current directory.
        if not os.path.exists(notebook_name):
            raise FileNotFoundError(
                f"The notebook {notebook_name} does not exist.")
            
        # Store the notebook's name, Markdown, and Python paths for later conversion.
        self.notebook_name = notebook_name
        self.path_md = path_md
        self.path_py = path_py
        self.conversions = conversions
        
        # Automatically convert the notebook to Markdown and Python formats.
        if 'md' in self.conversions:
            self.to_markdown()
        if 'py' in self.conversions:
            self.to_python()

    def _export_to_format(self, exporter, output_path):
        
        # Read the notebook's content and convert it to the desired format.
        body, _ = exporter.from_notebook_node(
            nbformat.read(self.notebook_name, as_version=4))
        
        # Write the converted content to the specified output path.
        with open(output_path, "w") as f:
            f.write(body)

    def to_markdown(self):

        # If no Markdown path is provided, set a default path as 'README.md' in the current directory.
        if not self.path_md:
            self.path_md = os.path.join(os.getcwd(), 'README.md')
            
        # Use the MarkdownExporter to convert the notebook to Markdown format.
        exporter = MarkdownExporter()
        self._export_to_format(exporter, self.path_md)
        
        print(f"Exported to markdown at {self.path_md}")

    def to_python(self):

        # If no Python script path is provided, derive it from the notebook's name.
        if not self.path_py:
            notebook_basename = os.path.splitext(self.notebook_name)[0]
            self.path_py = os.path.join(os.getcwd(), f'{notebook_basename}.py')
            
        # Use the PythonExporter to convert the notebook to a Python script format.
        exporter = PythonExporter()
        self._export_to_format(exporter, self.path_py)
        
        print(f"Exported to python script at {self.path_py}")
