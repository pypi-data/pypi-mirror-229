import os
import nbformat
from nbconvert import PythonExporter, MarkdownExporter

class NotebookConverter:
    """
    Converts Jupyter notebooks to various formats including Markdown 
    and Python.

    This class enables the conversion of Jupyter notebooks 
    (.ipynb files) into desired formats, primarily Markdown (.md) and 
    Python (.py) script files. 
    The user can provide specific paths for the output or default paths 
    will be used based on the notebook name.

    Attributes:
        notebook_name (str): Name of the Jupyter notebook to be 
        converted.
        path_md (str, optional): Desired output path for the Markdown 
        file. Defaults to 'README.md' in the current directory.
        path_py (str, optional): Desired output path for the Python 
        script. Defaults to a '.py' file with the same base name as the 
        notebook in the current directory.
        conversions (list, optional): List of desired output formats. 
        Supported values are 'md' and 'py'. Defaults to both 
        ['md', 'py'].

    Raises:
        FileNotFoundError: If the specified notebook does not exist in 
        the current directory.

    Methods:
        export_format(): Converts the notebook content to a specified 
        format and writes it to a file.
        to_markdown(): Converts the notebook to a Markdown format and 
        writes to the specified or default path.
        to_python(): Converts the notebook to a Python script and 
        writes to the specified or default path.
    """

    def __init__(self, conversions=['md', 'py'], notebook_name=None, 
                 path_md=None, path_py=None):
        
        # If the provided notebook_name doesn't have a '.ipynb' 
        # extension, add it.
        if not notebook_name.endswith('.ipynb'):
            notebook_name += '.ipynb'
        
        # Check if the notebook exists in the current directory.
        if not os.path.exists(notebook_name):
            raise FileNotFoundError(
                f"The notebook {notebook_name} does not exist.")
            
        # Store the notebook's name, Markdown, and Python paths for 
        # later conversion.
        self.notebook_name = notebook_name
        self.path_md = path_md
        self.path_py = path_py
        self.conversions = conversions
        
        # Automatically convert the notebook to Markdown and Python 
        # formats.
        if 'md' in self.conversions:
            self.to_markdown()
        if 'py' in self.conversions:
            self.to_python()

    def export_to_format(self, exporter, output_path):
        """
        Converts the notebook content to a specified format and writes 
        it to a file.

        Given an exporter (either for Markdown or Python) and an output 
        path, this private method reads the notebook's content, converts 
        it to the desired format, and writes the converted content to 
        the specified output path.

        Args:
            exporter (nbconvert.Exporter): An instance of a notebook 
            exporter, either MarkdownExporter or PythonExporter.
            output_path (str): Path where the converted notebook 
            content should be saved.

        Note:
            This is a private method and should not be called directly. 
            It's used by the `to_markdown` and `to_python` methods.
        """        
        # Read the notebook's content and convert it to the desired 
        # format.
        body, _ = exporter.from_notebook_node(
            nbformat.read(self.notebook_name, as_version=4))
        
        # Write the converted content to the specified output path.
        with open(output_path, "w") as f:
            f.write(body)

    def to_markdown(self):
        """
        Converts the notebook to Markdown format.

        If no output path for the Markdown file is provided during the 
        class instantiation, it defaults to 'README.md' in the current 
        directory. The method uses the MarkdownExporter from the 
        `nbconvert` module to perform the conversion.

        Raises:
            FileNotFoundError: If the specified notebook does not exist.

        Returns:
            None. The converted content is written to the specified or 
            default path.
        """
        # If no Markdown path is provided, set a default path as 
        # 'README.md' in the current directory.
        if not self.path_md:
            self.path_md = os.path.join(os.getcwd(), 'README.md')
            
        # Use the MarkdownExporter to convert the notebook to 
        # Markdown format.
        exporter = MarkdownExporter()
        self.export_to_format(exporter, self.path_md)
        
        print(f"Exported to markdown at {self.path_md}")

    def to_python(self):
        """
        Converts the notebook to a Python script format.

        If no output path for the Python script is provided during the 
        class instantiation, it derives one from the notebook's name. 
        The method uses the PythonExporter from the `nbconvert` module 
        to perform the conversion.

        Raises:
            FileNotFoundError: If the specified notebook does not exist.

        Returns:
            None. The converted content is written to the specified or 
            default path.
        """

        # If no Python script path is provided, derive it from the 
        # notebook's name.
        if not self.path_py:
            notebook_basename = os.path.splitext(self.notebook_name)[0]
            self.path_py = os.path.join(
                os.getcwd(), f'{notebook_basename}.py')
            
        # Use the PythonExporter to convert the notebook to a Python 
        # script format.
        exporter = PythonExporter()
        self.export_to_format(exporter, self.path_py)
        
        print(f"Exported to python script at {self.path_py}")
