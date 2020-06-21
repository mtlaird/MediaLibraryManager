from MediaLibraryManager.Sql.Main import create_database
from MediaLibraryManager.Sql.Scanning import DirectoryScan
from MediaLibraryManager.config import MediaLibraryManagerConfig, set_up_logging

import sys


if __name__ == '__main__':
    config = MediaLibraryManagerConfig()
    logger = set_up_logging(config)
    logger.info("Loaded config from {} ...".format(config.filename))
    database_name = config.db_name
    logger.info("Connecting to database '{}' ...".format(database_name))
    Session = create_database(database_name)
    session = Session()

    if len(sys.argv) > 1:
        directory_name = sys.argv[1]
    else:
        directory_name = 'F:/Pictures/Images/Photos'

    logger.info("Creating scan object ...")
    scan = DirectoryScan(directory_name)
    scan.logger = logger
    scan.log_file = config.generate_logfile_name()
    scan.destination = config.dest_dir
    scan.move_type = config.move_type
    get_md5 = config.get_md5
    scan.run_scan(get_md5, session)
    if (scan.move_type not in [None, "none"]) and scan.destination is not None:
        scan.copy_files(session)
        scan.add_images_to_db(session)
    else:
        scan.add_directory_to_db(session)
        scan.add_images_to_db(session, scanned_files=True)
    scan.add_scan_to_db(session)

    logger.info("Complete!")
