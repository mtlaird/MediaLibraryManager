import logging
import time

from MediaLibraryManager.Sql.Main import create_database
from MediaLibraryManager.Sql.Scanning import DirectoryScan
from MediaLibraryManager.config import MediaLibraryManagerConfig

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
    config = MediaLibraryManagerConfig()
    logfile_name = "{}/MLM-{}.log".format(config.log_dir, trunc(time.time()))
    logger = set_up_logging(logfile_name)
    logger.info("Loaded config from {} ...".format(config.filename))
    database_name = config.db_name

    logger.info("Connecting to database '{}' ...".format(database_name))
    Session = create_database(database_name)
    session = Session()

    if len(sys.argv) > 1:
        directory_name = sys.argv[1]
    else:
        directory_name = 'TestFolder'

    logger.info("Creating scan object ...")
    scan = DirectoryScan(directory_name)
    scan.logger = logger
    scan.log_file = logfile_name
    scan.destination = config.dest_dir
    scan.move_type = config.move_type
    get_md5 = False
    scan.run_scan(get_md5, session)
    scan.copy_files(session)
    scan.add_images_to_db(session)
    scan.add_scan_to_db(session)

    logger.info("Complete!")
