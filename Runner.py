import logging
import time

from MediaLibraryManager.Sql.Main import create_database
from MediaLibraryManager.Sql.Scanning import DirectoryScan

from math import trunc
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
    database_name = 'db'
    logfile_name = "logs/MLM-{}.log".format(trunc(time.time()))
    logger = set_up_logging(logfile_name)

    logger.info("Connecting to database '{}' ...".format(database_name))
    Session = create_database(database_name)
    session = Session()

    if len(sys.argv) > 1:
        directory_name = sys.argv[1]
    else:
        directory_name = 'TestFolder'
    if len(sys.argv) > 2:
        destination_directory = sys.argv[2]
    else:
        destination_directory = 'dstFolder'

    logger.info("Creating scan object ...")
    scan = DirectoryScan(directory_name)
    scan.logger = logger
    scan.log_file = logfile_name
    scan.destination = destination_directory
    scan.move_type = "keep"
    get_md5 = False
    scan.run_scan(get_md5, session)
    scan.copy_files(session)
    scan.add_images_to_db(session)
    scan.add_scan_to_db(session)

    logger.info("Complete!")
