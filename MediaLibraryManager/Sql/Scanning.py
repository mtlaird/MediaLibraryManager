import logging
import time

from sqlalchemy import Column, Integer, String

from MediaLibraryManager.Sql.FileSystem import DirectorySql
from MediaLibraryManager.Sql.Main import Base


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
        try:
            self.directory = DirectorySql(path)
        except NotADirectoryError:
            raise
        self.path = path
        self.files_found = 0
        self.subdirs_found = 0