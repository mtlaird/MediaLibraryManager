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
    logfile_name = "MLM-{}.log".format(trunc(time.time()))
    logger = set_up_logging(logfile_name)

    logger.info("Connectiong to database '{}' ...".format(database_name))
    Session = create_database(database_name)
    session = Session()

    directory_name = sys.argv[1]

    logger.info("Creating scan object ...")
    scan = DirectoryScan(directory_name)
    scan.logger = logger
    scan.log_file = logfile_name
    scan.run_scan(session)
    scan.add_scan_to_db(session)

    logger.info("Complete!")
