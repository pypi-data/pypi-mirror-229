'''
Entry point of the library for website backends and CLI applications.
'''
import logging, coloredlogs
from .main import Main
from . import convert

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

def main():
    logger.info('========= Starting conversion using jupdoc CLI =========')
    args = convert.parse()
    main_obj = Main()
    logger.info('========= Finished conversion using jupdoc CLI =========')



if __name__ == '__main__':
    main()