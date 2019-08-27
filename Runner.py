import logging

from MediaLibraryManager.Abstract.FileSystemAbstract import Directory
from MediaLibraryManager.Sql.Main import create_database
from MediaLibraryManager.util import *
import sys


def set_up_logging(f):
    log = logging.getLogger("MediaLibraryManager")
    handler = logging.FileHandler(f)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.setLevel(logging.INFO)
    log.addHandler(handler)

    return log


if __name__ == '__main__':
    logger = set_up_logging("MLM.log")

    Session = create_database('db')
    session = Session()

    directory_name = sys.argv[1]

    logger.info("Creating directory object for directory \"{dir}\" ...".format(dir=directory_name))
    directory = Directory(directory_name)

    logger.info("Total directory size: {}".format(convert_bytes_to_friendly_size(directory.get_total_size())))
    logger.info("Total files: {}".format(directory.get_total_files()))

    logger.info("Adding files to database ...")
    directory.add_files_to_db(session)

    logger.info("Complete!")
