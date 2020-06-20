import toml


class MediaLibraryManagerConfig:
    def __init__(self, filename=None):
        if not filename:
            filename = 'mlm-config.toml'
        self.filename = filename
        self.log_dir = 'logs'
        self.dest_dir = 'dstFolder'
        self.move_type = 'keep'
        self.db_name = 'db'
        with open(self.filename) as f:
            self.toml = toml.load(f)

        self.parse_toml()

    def parse_toml(self):
        if 'log_dir' in self.toml['config']:
            self.log_dir = self.toml['config']['log_dir']
        if 'dest_dir' in self.toml['config']:
            self.dest_dir = self.toml['config']['dest_dir']
        if 'move_type' in self.toml['config']:
            self.move_type = self.toml['config']['move_type']
        if 'db_name' in self.toml['config']:
            self.db_name = self.toml['config']['db_name']
