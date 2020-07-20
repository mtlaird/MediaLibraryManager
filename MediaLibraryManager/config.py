import logging
import time
from math import trunc

import toml


def set_up_logging(config, single_run=True):
    log = logging.getLogger("MediaLibraryManager")
    logfile_name = config.generate_logfile_name(single_run)
    handler = logging.FileHandler(logfile_name)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if config.log_level.lower() == 'info':
        log.setLevel(logging.INFO)
    elif config.log_level.lower() == 'error':
        log.setLevel(logging.ERROR)
    elif config.log_level.lower() == 'debug':
        log.setLevel(logging.DEBUG)
    log.addHandler(handler)

    return log


class MediaLibraryManagerConfig:

    class DirectoryConfig:

        def __init__(self, config):

            self.path = config['path']
            self.move_type = 'keep' if 'move_type' not in config else config['move_type']
            self.ignored_filetypes = [] if 'ignored_filetypes' not in config else config['ignored_filetypes']
            self.get_md5 = False if 'get_md5' not in config else config['get_md5']

    def __init__(self, filename=None):
        if not filename:
            filename = 'mlm-config.toml'
        self.filename = filename
        self.log_dir = 'logs'
        self.log_level = 'info'
        self.dest_dir = 'dstFolder'
        self.db_name = 'db'
        self.thumbnail_dir = 'thumbnails'
        self.directories = {}
        self.web_port = 5056
        with open(self.filename) as f:
            self.toml = toml.load(f)

        self.parse_toml()

    def parse_toml(self):
        if 'log_dir' in self.toml['config']:
            self.log_dir = self.toml['config']['log_dir']
        if 'log_level' in self.toml['config']:
            self.log_level = self.toml['config']['log_level']
        if 'dest_dir' in self.toml['config']:
            self.dest_dir = self.toml['config']['dest_dir']
        if 'db_name' in self.toml['config']:
            self.db_name = self.toml['config']['db_name']
        if 'thumbnail_dir' in self.toml['config']:
            self.thumbnail_dir = self.toml['config']['thumbnail_dir']
        if 'port' in self.toml['webapp']:
            self.web_port = self.toml['webapp']['port']

        for directory in self.toml['directories']:
            self.directories[directory] = self.DirectoryConfig(self.toml['directories'][directory])

    def generate_logfile_name(self, single_run=True):
        if single_run:
            return "{}/MLM-{}.log".format(self.log_dir, trunc(time.time()))
        else:
            return "{}/MLM.log".format(self.log_dir)
