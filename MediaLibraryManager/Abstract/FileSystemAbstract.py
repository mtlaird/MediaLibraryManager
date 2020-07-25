# from os.path import isdir, isfile
# from os import listdir
# from MediaLibraryManager.Sql.FileSystem import FileSql
#
#
# class Directory:
#
#     def __init__(self, path):
#
#         if '\\' in path:
#             path = path.replace('\\', '/')
#
#         self.files = {}
#         self.directories = {}
#         if isdir(path):
#             self.path = path
#             self.get_dir_contents()
#
#             self.size = self.get_total_size()
#
#     def get_dir_contents(self):
#
#         contents = listdir(self.path)
#         for c in contents:
#
#             full_path = self.path + '/' + c
#
#             if isdir(full_path):
#                 self.directories[c] = Directory(full_path)
#             elif isfile(full_path):
#                 self.files[c] = FileSql(full_path)
#
#     def get_total_size(self):
#
#         size = 0
#
#         for f in self.files:
#             size += self.files[f].size
#
#         for d in self.directories:
#             size += self.directories[d].size
#
#         return size
#
#     def get_total_files(self):
#
#         files = len(self.files)
#
#         for d in self.directories:
#             files += self.directories[d].get_total_files()
#
#         return files
#
#     def add_files_to_db(self, session):
#
#         for f in self.files:
#             self.files[f].add_to_db(session)
#
#         for d in self.directories:
#             self.directories[d].add_files_to_db(session)
