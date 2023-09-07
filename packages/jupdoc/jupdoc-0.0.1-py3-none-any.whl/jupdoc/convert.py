import os
import yaml
import argparse
import sys
import nbformat
import logging, coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

def read_notebook(filename):
    """
    Read a notebook from a file.
    """
    with open(filename, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    return nb

def initialize_copies(notebook, tags):
    """
    tags is a list of cell tags in higher to lower inclusion order, higher includes all lower and so on
    """
    copies = {}
    for tag in tags:
        copies[tag] = notebook.copy()
        if tag != 'report' and tag != 'master': 
            copies[tag].cells = []
    return copies


def populate_copies(copies, notebook, tags):
    """
    tags is a list of cell tags in higher to lower inclusion order, higher includes all lower and so on
    """
    for cell in notebook.cells:
        if "tags" not in cell.metadata.keys():
            pass
        else:
            if cell.metadata.tags == []:
                pass
            else:
                index = [idx for idx, x in enumerate(tags) if x in cell.metadata.tags]
                list_tgs = tags[1: index[0]+1]
                for i in range(len(list_tgs)):
                    copies[list_tgs[i]].cells.append(cell)
    return copies

def write_notebook(notebook, filename, path='./docs', format='docx'):
    """
    Write a notebook to a file in the specified format, using quatro 
    """
    final_nb_path = os.path.join(path, filename + '.ipynb')
    final_path = os.path.join(path, filename + '.' + format)
    nbformat.write(notebook, final_nb_path)
    os.system('quarto render ' + final_nb_path + ' --to ' + format) 
    os.remove(final_nb_path)

def parse():
    """
    Parses CLI arguments or config YAML file.
    """
    parser = argparse.ArgumentParser(description='Convert a notebook to a report')
    parser.add_argument('--config', type=str, default=None, help='config file')

    args = parser.parse_args()

    if args.config is not None:
        with open(args.config, 'r') as config_file:
            yml_cfg = yaml.safe_load(config_file)
            if yml_cfg:
                return argparse.Namespace(**yml_cfg)
            else:
                logger.error("Failed to load configuration from the provided YAML file.")
                # raise ValueError("Failed to load configuration from the provided YAML file.")
    else:
        parser.add_argument('--filename', type=str, default='notebook.ipynb', help='filename of the notebook')
        parser.add_argument('--tags', nargs='+', type=str, default=['master', 'report'], help='tags to include in the report')
        parser.add_argument('--prefix', type=str, default='report', help='prefix for the report filename')
        parser.add_argument('--output', type=str, default='./docs', help='output directory')
        parser.add_argument('--format', type=str, default='docx', help='output format')
        args = parser.parse_args()
        return args

def main(args):
    nb = read_notebook(args.filename)
    copies = initialize_copies(nb, args.tags)
    copies = populate_copies(copies, nb, args.tags)
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    for tag in args.tags:
        write_notebook(copies[tag], 
                       args.prefix + tag, args.output, args.format)
        
if __name__ == '__main__':
    args = parse()
    main(args)