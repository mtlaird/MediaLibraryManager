import logging
import time

from sqlalchemy import Column, Integer, String
from PIL import UnidentifiedImageError

from MediaLibraryManager.Sql.FileSystem import DirectorySql
from MediaLibraryManager.Sql.Main import Base
from MediaLibraryManager.Sql.LibraryImage import LibraryImage
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
    images_added = Column(Integer)
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
        self.files_moved_list = []
        self.images_added_list = []

    def directory_init(self, get_md5=False, session=None):

        if session:
            self.directory = session.query(DirectorySql).filter(DirectorySql.path == self.path).one_or_none()

        if not self.directory:
            try:
                self.directory = DirectorySql(self.path)
            except NotADirectoryError:
                raise
        else:
            self.directory.__init__(self.path)
        self.directory.run_scan(get_md5)

    def run_scan(self, get_md5=False, session=None):

        self.logger.info("Creating directory object for directory \"{dir}\" ...".format(dir=self.path))
        self.directory_init(get_md5, session)

        self.logger.info("Total directory size: {}".format(
            convert_bytes_to_friendly_size(self.directory.get_total_size())))
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

    def copy_files(self, session):

        self.logger.info("Copying files to {} ...".format(self.destination))

        if self.move_type == "flatten":
            self.files_moved_list = self.directory.copy_files_to_new_path(self.destination, session)
        elif self.move_type == "managed":
            self.files_moved_list = self.directory.copy_files_to_managed_path(self.destination, session)
        else:
            self.files_moved_list = self.directory.copy_directory_to_new_path(self.destination, session)

        self.files_moved = len(self.files_moved_list)
        self.logger.info("Copied {} files.".format(self.files_moved))
        return self.files_moved

    def add_images_to_db(self, session):
        self.logger.info("Adding images to db...")
        for f in self.files_moved_list:
            try:
                i = LibraryImage(f.id, f.path + f.filename)
                self.logger.debug("Successfully created image from file: {}".format(f.path + f.filename))
            except UnidentifiedImageError:
                self.logger.debug("Failed to create image from file: {}".format(f.path + f.filename))
            else:
                i.add_to_db(session)
                self.images_added_list.append(i)

        self.images_added = len(self.images_added_list)
        self.logger.info("Added {} images.".format(self.images_added))
        return self.images_added_list
