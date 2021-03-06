import hashlib
import logging
import shutil
import time
import urllib.parse
from datetime import datetime as dt
from os import stat, listdir, mkdir
from os.path import isfile, isdir

import humanfriendly
from sqlalchemy import Column, Integer, String, ForeignKey

from MediaLibraryManager.Sql.Main import Base, BaseMixin
from MediaLibraryManager.Sql.FileTags import FileTag, Tag
from MediaLibraryManager.util import *


class File(BaseMixin, Base):

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
    scan_id = Column(Integer, ForeignKey('directoryscan.id'))

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
            self.scan_id = None
            if not get_md5:
                self.md5 = None
            else:
                self.md5 = self.get_md5sum()
            if '.' in self.filename:
                self.extension = self.filename.split('.')[-1]
            else:
                self.extension = None
        else:
            print("File {} does not exist!".format(path))
            raise FileNotFoundError

    def get_friendly_size(self):

        return humanfriendly.format_size(self.size)

    @staticmethod
    def convert_friendly_time(ts_int):

        ts = dt.fromtimestamp(ts_int)
        return ts.strftime("%B %d, %Y %H:%M:%S")

    def get_friendly_created_time(self):

        return self.convert_friendly_time(self.ctime)

    def check_in_db(self, session, include_md5=False):

        if not include_md5:
            r = session.query(File).\
                filter(File.filename == self.filename).\
                filter(File.path == self.path)
        else:
            r = session.query(File).\
                filter(File.filename == self.filename).\
                filter(File.path == self.path).\
                filter(File.md5 == self.md5)

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

    def copy_file_to_new_path(self, new_path, session=None, scan_id=None):
        current_path = self.path + self.filename
        shutil.copy2(current_path, new_path)

        if session:
            new_file = File(new_path + "/" + self.filename)
            new_file.orig_filename = self.filename
            new_file.orig_path = self.path
            new_file.scan_id = scan_id if scan_id else None
            new_file.add_to_db(session)
            return new_file

    def copy_file_to_managed_path(self, new_path, session=None, scan_id=None):
        current_path = self.path + self.filename
        if not self.md5:
            raise TypeError
        new_filename = self.md5 + "." + self.extension
        new_directory = new_path + "/" + self.md5[0:2] + "/"

        if not isdir(new_directory):
            mkdir(new_directory)

        new_path = new_directory + new_filename
        shutil.copy2(current_path, new_path)

        if session:
            new_file = File(new_path, get_md5=True)
            new_file.orig_filename = self.filename
            new_file.orig_path = self.path
            new_file.scan_id = scan_id if scan_id else None
            new_file.add_to_db(session)
            return new_file

    def get_tags(self, session):

        return FileTag.get_tags_by_file_id(session, self.id)

    def add_tag_by_id(self, session, tag_id):

        self._add_tag(session, tag_id)

    def add_tag_by_values(self, session, tag_name, tag_value):

        tag = Tag.get_or_create(session, tag_name, tag_value)
        self._add_tag(session, tag.id)

    def _add_tag(self, session, tag_id):

        file_tag = FileTag(file_id=self.id, tag_id=tag_id)
        session.add(file_tag)
        session.commit()

    def compare_mtime(self, mtime=None):

        if not mtime:
            return True

        if mtime < self.mtime:
            return True

        return False


class Directory(BaseMixin, Base):

    path = Column(String)
    times_scanned = Column(Integer)
    last_scan_time = Column(Integer)
    files_scanned = Column(Integer)
    files_moved = Column(Integer)

    def __init__(self, path, ignored_filetypes=None):

        self.logger = logging.getLogger('MediaLibraryManager')

        if '\\' in path:
            path = path.replace('\\', '/')

        self.files = {}
        self.directories = {}
        self.size = 0
        self.files_moved_this_scan = 0
        if not self.last_scan_time:
            self.last_scan_time = 0
        if not self.files_moved:
            self.files_moved = 0
        if not ignored_filetypes:
            self.ignored_filetypes = []
        else:
            self.ignored_filetypes = ignored_filetypes
        if isdir(path):
            self.path = path
        else:
            raise NotADirectoryError

    def get_dir_contents(self, get_md5=False):

        contents = listdir(self.path)
        for c in contents:

            full_path = self.path + '/' + c

            if isdir(full_path):
                self.directories[c] = Directory(full_path, self.ignored_filetypes)
                self.directories[c].get_dir_contents(get_md5)
            elif isfile(full_path):
                if full_path.split('.')[-1] not in self.ignored_filetypes:
                    self.files[c] = File(full_path, get_md5)

    def get_all_files(self):
        files_list = []

        for f in self.files:
            files_list.append(self.files[f])
        for d in self.directories:
            files_list += self.directories[d].get_all_files()

        return files_list

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

    def run_scan(self, get_md5=False):

        self.get_dir_contents(get_md5)
        self.size = self.get_total_size()

    def add_files_to_db(self, session, scan_id=None):

        for f in self.files:
            if scan_id:
                self.files[f].scan_id = scan_id
            self.files[f].add_to_db(session)

        for d in self.directories:
            self.directories[d].add_files_to_db(session, scan_id)

    def custom_pre_add(self, session):

        if not self.id:
            self.times_scanned = 1
            self.files_scanned = self.get_total_files()
        else:
            self.times_scanned += 1
            if self.files_scanned is None:
                self.files_scanned = self.get_total_files()
            else:
                self.files_scanned += self.get_total_files()

    def get_subdir(self, base_path):

        if base_path in self.path:
            subdir = self.path.replace(base_path, '')
            return subdir
        else:
            return self.path

    # Copies files into a new directory, while preserving subdirectory structure
    def copy_directory_to_new_path(self, new_path, session=None, scan_id=None, last_scan_time=None):

        if not last_scan_time:
            last_scan_time = self.last_scan_time
        self.logger.info("adding directory '{}' ...".format(self.path))
        if not isdir(new_path):
            mkdir(new_path)

        for f in self.files:
            if self.files[f].mtime > last_scan_time:
                self.logger.info("adding file '{}' ...".format(f))
                self.files[f].copy_file_to_new_path(new_path, session, scan_id)
                self.increment_files_moved(1)
            else:
                self.logger.info("skipping file '{}' due to mtime: {} is less than {}".
                                 format(f, trunc(self.files[f].mtime), last_scan_time))

        for d in self.directories:
            subdir = self.directories[d].get_subdir(self.path)
            self.directories[d].copy_directory_to_new_path(new_path + subdir, session, scan_id, last_scan_time)
            self.increment_files_moved(self.directories[d].files_moved_this_scan)

    # Copies all files into a new directory, without preserving subdirectory structure
    def copy_files_to_new_path(self, new_path, session=None, scan_id=None, last_scan_time=None):

        if not last_scan_time:
            last_scan_time = self.last_scan_time
        if not isdir(new_path):
            mkdir(new_path)

        for f in self.files:
            if self.files[f].mtime < last_scan_time:
                self.files[f].copy_file_to_new_path(new_path, session, scan_id)
                self.increment_files_moved(1)
            else:
                self.logger.info("skipping file '{}' due to mtime: {} is less than {}".
                                 format(f, trunc(self.files[f].mtime), last_scan_time))

        for d in self.directories:
            self.directories[d].copy_files_to_new_path(new_path, session, scan_id, last_scan_time)
            self.increment_files_moved(self.directories[d].files_moved_this_scan)

    # Copies all files into a new directory, managing the subdirectory structure using file hashes
    def copy_files_to_managed_path(self, new_path, session=None, scan_id=None, last_scan_time=None):

        if not last_scan_time:
            last_scan_time = self.last_scan_time
        if not isdir(new_path):
            mkdir(new_path)

        for f in self.files:
            if self.files[f].mtime < last_scan_time:
                try:
                    self.files[f].copy_file_to_managed_path(new_path, session, scan_id)
                    self.increment_files_moved(1)
                except TypeError:
                    self.logger.error("Could not copy file {} - no md5 found!".format(f))
            else:
                self.logger.info("skipping file '{}' due to mtime: {} is less than {}".
                                 format(f, trunc(self.files[f].mtime), last_scan_time))

        for d in self.directories:
            self.directories[d].copy_files_to_managed_path(new_path, session, scan_id, last_scan_time)
            self.increment_files_moved(self.directories[d].files_moved_this_scan)

    def increment_files_moved(self, num_files):

        if not self.files_moved_this_scan:
            self.files_moved_this_scan = num_files
        else:
            self.files_moved_this_scan += num_files

    def get_url_encoded_path(self):

        return urllib.parse.quote_plus(self.path)
