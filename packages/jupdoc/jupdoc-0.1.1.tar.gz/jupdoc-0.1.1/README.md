# JupDoc: Streamlining Conversion of Jupyter Notebooks to Qurato Supported Formats with multiple User-Levels 🚀

[![PyPI Version](https://img.shields.io/pypi/v/jupdoc.svg)](https://pypi.org/project/jupdoc/)
[![Python Versions](https://img.shields.io/pypi/pyversions/jupdoc.svg)](https://pypi.org/project/jupdoc/)
[![License](https://img.shields.io/pypi/l/jupdoc.svg)](https://pypi.org/project/jupdoc/)
[![Downloads](https://pepy.tech/badge/jupdoc)](https://pepy.tech/project/jupdoc)
[![Downloads](https://pepy.tech/badge/jupdoc/month)](https://pepy.tech/project/jupdoc/month)
[![Downloads](https://pepy.tech/badge/jupdoc/week)](https://pepy.tech/project/jupdoc/week)

JupDoc is a Python package that simplifies the process of converting Jupyter Notebooks into multiple docx files (or other Quarto supported formats) while applying role-based access control based on cell tags.

## Table of Contents
- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [To Do](#to-do)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contributing](#contributing)


_Please note that this package is still under development, and the documentation is not complete. There may be bugs and the API may change._

## About
JupDoc is a Python package that simplifies the process of converting Jupyter Notebooks into multiple docx files or other formats while applying role-based access control based on cell tags. It is based on [Quarto](https://quarto.org/). The package is designed to be used in a JupyterHub environment where multiple users can access the same notebook. The package allows the user to define access roles using cell tags. The package then generates separate documents for each access role. The package can be used as a command line tool or as a python API.

The current version of the package supports the following formats:
- .ipynb (Jupyter Notebook) to .docx (Microsoft Word Document)
- .ipynb (Jupyter Notebook) to .pdf (Portable Document Format)
- .ipynb (Jupyter Notebook) to .html (Hypertext Markup Language)
- .ipynb (Jupyter Notebook) to .tex (LaTeX Document)
- .ipynb (Jupyter Notebook) to .md (Markdown Document)

The package also supports uploading the generated files to Google Drive. The package can be used with a Google Drive Service Account. The package can also be used without uploading the files to Google Drive.

## Features

- Convert Jupyter Notebooks to docx, PDF, HTML, and more.
- Define access roles using cell tags.
- Generate separate documents for each access role.

## Installation

You can install JupDoc using pip:
```bash
pip install jupdoc
```
JupDoc is based on Quarto to convert ipynb files to other formats. The instructions to install quarto can be found [here](https://quarto.org/docs/getting-started/installation.html).
## Usage
We support two ways to convert notebooks to docs. The first one is using the command line interface. The second one is using the python API.

*Note:* 
1. _The conversion of .ipynb is based on Quarto and custom rending can be done by adding yaml config specific to notebooks as raw cells._
2. _All cells in the notebook should have tags (including markdown cells), and the tags should be a part of the config used to export._
3. _Quarto cheat sheet can be refered from [here](https://images.datacamp.com/image/upload/v1676540721/Marketing/Blog/Quarto_Cheat_Sheet.pdf). Details can be provided in the raw cell for customisations on reports._

### Command Line Interface
The command line interface can be used as follows:
```bash
jupdoc --config <config_file>
```
In case of absence of the config file, the configs can be passed as command line arguments:
```bash
jupdoc --filename <filename> --tags <tags> --prefix <prefix> --output <output> --format <format> --upload <upload> --folder_url <folder_url> --creds_path <creds_path> --reference_docx <reference_docx>
```
The arguments are as follows:
- `filename`: The path to the notebook file.
- `tags`: The tags to be used for access control. Multiple tags can be passed as a comma-separated string.
- `prefix`: The prefix to be used for the output files.
- `output`: The path to the output directory.
- `format`: File format to be exported to. 
- `upload`: Upload the files to Google Drive.
- `folder_url`: The URL of the Google Drive folder to upload the files to.
- `creds_path`: The path to the Google Drive credentials file. (For Service Account)
- `reference_docx`: The path to the reference docx file. (Optional)
### Python API
The python API can be used as follows:
```python
from jupdoc import convert
args = {
    "filename": "notebook.ipynb",
    "tags": ["tag1", "tag2"],
    "prefix": "prefix",
    "output": "output",
    "format": "docx",
    "upload": True,
    "folder_url": "https://drive.google.com/drive/folders/1Qlw7SxdPr4Ag1mKl4-cTrjgJPgZyzzYb?usp=drive_link",
    "creds_path": "creds.json"
    "reference_docx": "reference.docx"

}
convert(**args)
```
## To Do
1. Improve documentation. _On-Going_
2. Add support for multiple cell tags.
3. GitHub Actions to generate reports on push, based on JupDoc configs.
## License
This project is licensed under the terms of the MIT license.
## Acknowledgements
This project is based on [Quarto](https://quarto.org/).
## Contributing
Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.
You can contribute in many ways:
- Report bugs.
- Fix bugs and submit pull requests.
- Write, clarify, or fix documentation.
- Suggest or add new features.
---