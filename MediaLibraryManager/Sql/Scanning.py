import logging
import time

from sqlalchemy import Column, Integer, String

from MediaLibraryManager.Sql.FileSystem import DirectorySql
from MediaLibraryManager.Sql.Main import Base
from MediaLibraryManager.util import *


class DirectoryScan(Base):
    __tablename__ = 'directory_scans'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    start_time = Column(Integer)
    end_time = Column(Integer)
    files_found = Column(Integer)
    subdirs_found = Column(Integer)
    destination = Column(String)
    files_moved = Column(Integer)
    move_type = Column(String)
    log_file = Column(String)

    def __init__(self, path):
        self.logger = logging.getLogger('MediaLibraryManager')
        self.start_time = int(time.time())
        self.path = path
        self.directory = None
        self.files_found = 0
        self.subdirs_found = 0
        self.total_size = 0
        self.logger = None

    def directory_init(self, session=None):

        if session:
            self.directory = session.query(DirectorySql).filter(DirectorySql.path == self.path).one_or_none()

        if not self.directory:
            try:
                self.directory = DirectorySql(self.path)
            except NotADirectoryError:
                raise
        self.directory.run_scan()

    def run_scan(self, session=None):

        self.logger.info("Creating directory object for directory \"{dir}\" ...".format(dir=self.path))
        self.directory_init(session)

        self.logger.info("Total directory size: {}".format(convert_bytes_to_friendly_size(self.directory.get_total_size())))
        self.total_size = self.directory.get_total_size()
        self.logger.info("Total files: {}".format(self.directory.get_total_files()))
        self.files_found = self.directory.get_total_files()
        self.logger.info("Total subdirectories: {}".format(self.directory.get_total_subdirs()))
        self.subdirs_found = self.directory.get_total_subdirs()

    def add_scan_to_db(self, session):

        self.logger.info("Adding directory and files to database...")
        self.add_directory_to_db(session)
        self.logger.info("Adding scan to database...")
        self.end_time = trunc(time.time())
        self.add_to_db(session)

    def add_directory_to_db(self, session):

        self.directory.add_to_db(session)
        self.directory.add_files_to_db(session)

    def add_to_db(self, session):

        session.add(self)
        session.commit()
