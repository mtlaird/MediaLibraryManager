from MediaLibraryManager.Sql.Main import create_database
from MediaLibraryManager.Sql.Scanning import DirectoryScan
from MediaLibraryManager.config import MediaLibraryManagerConfig, set_up_logging


if __name__ == '__main__':
    config = MediaLibraryManagerConfig()
    logger, logfile_name = set_up_logging(config)
    logger.info("Loaded config from {} ...".format(config.filename))
    database_name = config.db_name
    logger.info("Connecting to database '{}' ...".format(database_name))
    Session = create_database(database_name)
    session = Session()

    logger.info("Found config for {} directories to scan ...".format(len(config.directories.keys())))
    for dir_key in config.directories.keys():
        dir_config = config.directories[dir_key]
        logger.info("Scanning directory with key '{}' ...".format(dir_key))
        logger.info("Creating scan object for directory '{}' ...".format(dir_config.path))
        scan = DirectoryScan(dir_config.path, dir_config.ignored_filetypes)
        scan.logger = logger
        scan.log_file = logfile_name
        scan.destination = config.dest_dir
        scan.move_type = dir_config.move_type
        scan.thumbnail_dir = config.thumbnail_dir
        scan.full_scan(session, dir_config.get_md5)

    logger.info("Complete!")
