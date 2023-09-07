from . import convert
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

class Main:
    def __init__(self):
        args = convert.parse()
        convert.main(args)

