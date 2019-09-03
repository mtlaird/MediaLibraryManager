import hashlib
import logging
import shutil
import time
from os import stat, listdir
from os.path import isfile, isdir
from sqlalchemy import Column, Integer, String

from MediaLibraryManager.Sql.Main import Base
from MediaLibraryManager.util import *


class FileSql(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    md5 = Column(String)
    filename = Column(String)
    size = Column(Integer)
    atime = Column(Integer)
    mtime = Column(Integer)
    ctime = Column(Integer)
    extension = Column(String)
    orig_path = Column(String)
    orig_filename = Column(String)

    def __init__(self, path, get_md5=False):

        self.logger = logging.getLogger('MediaLibraryManager')
        if isfile(path):
            self.full_path = path
            stat_results = stat(self.full_path)
            self.size = stat_results.st_size
            self.atime = stat_results.st_atime
            self.mtime = stat_results.st_mtime
            self.ctime = stat_results.st_ctime
            self.filename = self.full_path.split('/')[-1]
            self.path = '/'.join(self.full_path.split('/')[:-1]) + '/'
            if not get_md5:
                self.md5 = None
            else:
                self.md5 = self.get_md5sum()
            if '.' in self.filename:
                self.extension = self.filename.split('.')[-1]
            else:
                self.extension = None
        else:
            raise FileNotFoundError

    def add_to_db(self, session):

        if not self.id:
            session.add(self)
            session.commit()

    def check_in_db(self, session, include_md5=False):

        if not include_md5:
            r = session.query(FileSql).\
                filter(FileSql.filename == self.filename).\
                filter(FileSql.path == self.path)
        else:
            r = session.query(FileSql).\
                filter(FileSql.filename == self.filename).\
                filter(FileSql.path == self.path).\
                filter(FileSql.md5 == self.md5)

        if r.count() == 1:
            return True
        elif r.count() == 0:
            return False

    def get_md5sum(self):
        hash_md5 = hashlib.md5()
        with open(self.path + self.filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def set_md5sum(self, session):
        self.md5 = self.get_md5sum()
        session.add(self)
        session.commit()

    def human_readable_size(self):

        return convert_bytes_to_friendly_size(self.size)

    def human_readable_time(self, time_type):
        if time_type == 'atime':
            return convert_epoch_to_friendly_date(self.atime)
        elif time_type == 'mtime':
            return convert_epoch_to_friendly_date(self.mtime)
        elif time_type == 'ctime':
            return convert_epoch_to_friendly_date(self.ctime)

    def copy_file_to_new_path(self, new_path, session=None):
        current_path = self.path + self.filename
        shutil.copy2(current_path, new_path)

        if session:
            new_file = FileSql(new_path)
            new_file.orig_filename = self.filename
            new_file.orig_path = self.path
            new_file.add_to_db(session)


class DirectorySql(Base):

    __tablename__ = 'directories'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    times_scanned = Column(Integer)
    last_scan_time = Column(Integer)
    files_scanned = Column(Integer)
    files_moved = Column(Integer)

    def __init__(self, path):

        if '\\' in path:
            path = path.replace('\\', '/')

        self.files = {}
        self.directories = {}
        self.size = 0
        if isdir(path):
            self.path = path
        else:
            raise NotADirectoryError

    def get_dir_contents(self):

        contents = listdir(self.path)
        for c in contents:

            full_path = self.path + '/' + c

            if isdir(full_path):
                self.directories[c] = DirectorySql(full_path)
                self.directories[c].get_dir_contents()
            elif isfile(full_path):
                self.files[c] = FileSql(full_path)

    def get_total_size(self):

        size = 0

        for f in self.files:
            size += self.files[f].size

        for d in self.directories:
            size += self.directories[d].size

        return size

    def get_total_files(self):

        files = len(self.files)

        for d in self.directories:
            files += self.directories[d].get_total_files()

        return files

    def get_total_subdirs(self):

        subdirs = len(self.directories)

        for d in self.directories:
            subdirs += self.directories[d].get_total_subdirs()

        return subdirs

    def set_scan_time(self):

        self.last_scan_time = trunc(time.time())

    def run_scan(self):

        self.get_dir_contents()
        self.set_scan_time()
        self.size = self.get_total_size()

    def add_files_to_db(self, session):

        for f in self.files:
            self.files[f].add_to_db(session)

        for d in self.directories:
            self.directories[d].add_files_to_db(session)

    def add_to_db(self, session):

        if not self.id:
            self.times_scanned = 1
            self.files_scanned = self.get_total_files()
            self.files_moved = 0
        else:
            self.times_scanned += 1
            self.files_scanned += self.get_total_files()

        session.add(self)
        session.commit()
