import os
import yaml
import argparse
import sys
import nbformat
import logging
import coloredlogs
from . import upload

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


def read_notebook(filename):
    """
    description:
        Read a notebook from a file.
    args:
        filename: path to the notebook file
    output:
        nb: notebook object
    """
    with open(filename, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    return nb


def initialize_copies(notebook, tags):
    """
    description:
        tags is a list of cell tags in higher to lower inclusion order, higher includes all lower and so on
    args:
        notebook: notebook object
        tags: list of tags, defined in higher to lower inclusion order (specify master first, then report, etc.)
    output:
        copies: dictionary of notebook objects, based on total user roles defined in tags
    """
    notebook_copy = notebook.copy()
    default_raw_cell = nbformat.v4.new_raw_cell(source=r'---\ntitle: "Sample Document"\ndate: "2023-09-07"\nauthor: "Ashish Papanai"\nsubtitle: "This is a sample document generated using JupDoc" \n\nformat:\n  docx:\n    toc: true\n    toc-title: "Table of Contents"\n    number-sections: true\n    number-depth: 3\n    fig-align: center\n    code-line-numbers: true\n---')
    copies = {}
    for tag in tags:
        copies[tag] = notebook.copy()
        if tag != 'report' and tag != 'master':
            copies[tag].cells = []
            if len(notebook_copy.cells) > 0:
                if notebook_copy.cells[0].cell_type == 'raw':
                    copies[tag].cells.append(notebook_copy.cells[0])
                else:
                    copies[tag].cells.append(default_raw_cell)
            else: 
                copies[tag].cells.append(default_raw_cell)
        else: 
            if len(notebook_copy.cells) > 0:
                if notebook_copy.cells[0].cell_type == 'raw':
                    pass
                else:
                    copies[tag].cells = [default_raw_cell] + copies[tag].cells
            else:
                copies[tag].cells = [default_raw_cell]
                
    return copies


def populate_copies(copies, notebook, tags):
    """
    description:
        Populate the copies dictionary with cells from the notebook, based on tags (specified in higher to lower inclusion order)
    args:
        copies: dictionary of notebook objects, based on total user roles defined in tags
        notebook: notebook object
        tags: list of tags, defined in higher to lower inclusion order (specify master first, then report, etc.)
    output:
        copies: dictionary of notebook objects, based on total user roles defined in tags
    """
    for cell in notebook.cells:
        if "tags" not in cell.metadata.keys():
            pass
        else:
            if cell.metadata.tags == []:
                pass
            else:
                index = [idx for idx, x in enumerate(
                    tags) if x in cell.metadata.tags]
                list_tgs = tags[1: index[0]+1]
                for i in range(len(list_tgs)):
                    copies[list_tgs[i]].cells.append(cell)
    return copies


def write_notebook(args, notebook, filename, 
                   path='./docs', format='docx', 
                   folder_id=None, reference_docx=None):
    """
    description:
        Write a notebook to a file in the specified format, using quatro (https://quarto.org/docs/quick-start.html)
    args:
        notebook: notebook object
        filename: name of the file to be written
        path: path to the output directory
        format: output format
        folder_id: ID of the Google Drive folder to upload to
    output:
        None
    """
    final_nb_path = os.path.join(path, filename + '.ipynb')
    final_path = os.path.join(path, filename + '.' + format)
    if reference_docx != None:
        original_source = notebook.cells[0]['source']
        original_source = original_source[:-3]
        ref_add = 'reference-doc: ' + reference_docx + '\n---'
        notebook.cells[0]['source'] = original_source + '\n' + ref_add
        nbformat.write(notebook, final_nb_path)
        os.system('quarto render ' + final_nb_path + ' --to ' + format)
    else:
        nbformat.write(notebook, final_nb_path)
        os.system('quarto render ' + final_nb_path + ' --to ' + format)
    os.remove(final_nb_path)
    if args.upload and args.format == 'docx' and folder_id is not None:
        upload.upload_file(file_name=filename + '.' + format,
                           folder_id=folder_id,
                           local_path=path,
                           mime_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           creds_path=args.creds_path)
    elif args.upload and args.format == 'pdf' and folder_id is not None:
        upload.upload_file(file_name=filename + '.' + format,
                           folder_id=folder_id,
                           local_path=path,
                           mime_type='application/pdf',
                           creds_path=args.creds_path)
    elif args.upload and args.format == 'html' and folder_id is not None:
        upload.upload_file(file_name=filename + '.' + format,
                           folder_id=folder_id,
                           local_path=path,
                           mime_type='text/html',
                           creds_path=args.creds_path)
    else:
        logger.warning(
            "File not uploaded to Google Drive. Please check if the file format is supported or if the folder ID is correct.")


def parse():
    """
    description:
        Parses CLI arguments or config YAML file.
    args:
        None
    output:
        args: parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Convert a notebook to a report')
    parser.add_argument('--config', type=str, default=None, help='config file')

    args = parser.parse_args()

    if args.config is not None:
        with open(args.config, 'r') as config_file:
            yml_cfg = yaml.safe_load(config_file)
            if yml_cfg:
                return argparse.Namespace(**yml_cfg)
            else:
                logger.error(
                    "Failed to load configuration from the provided YAML file.")
                # raise ValueError("Failed to load configuration from the provided YAML file.")
    else:
        parser.add_argument(
            '--filename', type=str, default='notebook.ipynb', help='filename of the notebook')
        parser.add_argument('--tags', nargs='+', type=str,
                            default=['master', 'report'], help='tags to include in the report')
        parser.add_argument('--prefix', type=str, default='report',
                            help='prefix for the report filename')
        parser.add_argument('--output', type=str,
                            default='./docs', help='output directory')
        parser.add_argument('--format', type=str,
                            default='docx', help='output format')
        parser.add_argument('--upload', action='store_true',
                            help='upload to Google Drive')
        parser.add_argument('--folder_url', type=str,
                            default='https://drive.google.com/drive/folders/1Qlw7SxdPr4Ag1mKl4-cTrjgJPgZyzzYb?usp=drive_link',
                            help='URL of the Google Drive folder to upload to')
        parser.add_argument('--creds_path', type=str, default='./creds.json',
                            help='path to the Google Drive credentials file')
        parser.add_argument('--reference_docx', type=str, default=None, help='path to the reference docx file')
        args = parser.parse_args()
        args.folder_id = args.folder_url.split('/')[-1].split('?')[0]
        return args


def main(args):
    """
    description:
        Main function, calls other functions to convert a notebook to a report
    args:
        args: parsed arguments
    output:
        None
    """
    nb = read_notebook(args.filename)
    copies = initialize_copies(nb, args.tags)
    copies = populate_copies(copies, nb, args.tags)
    if args.folder_url is not None:
        folder_id = args.folder_url.split('/')[-1].split('?')[0]
    else:
        folder_id = None
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    for tag in args.tags:
        filename = args.prefix + tag if args.prefix is not None else tag
        write_notebook(args=args,
                       notebook=copies[tag],
                       filename=filename,
                       path=args.output,
                       format=args.format,
                       folder_id=folder_id,
                       reference_docx=args.reference_docx)

if __name__ == '__main__':
    args = parse()
    main(args)
