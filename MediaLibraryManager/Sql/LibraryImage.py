import logging

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from PIL import Image

from MediaLibraryManager.Sql.Main import Base

THUMBNAIL_MAX_SIZE = (150, 150)


class LibraryImage(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'))
    format = Column(String)
    height = Column(Integer)
    width = Column(Integer)
    thumbnail_path = Column(String)

    file_info = relationship('FileSql')

    def __init__(self, file_id, path):
        self.logger = logging.getLogger('MediaLibraryManager')

        self.image = Image.open(path)
        self.file_id = file_id
        self.format = self.image.format
        self.height = self.image.height
        self.width = self.image.width
        self.thumbnail_path = None

    def add_to_db(self, session):

        if not self.id:
            session.add(self)
            session.commit()

    def create_thumbnail(self, thumbnail_dir):

        if not thumbnail_dir:
            thumbnail_dir = 'thumbnails'

        self.image.thumbnail(THUMBNAIL_MAX_SIZE)
        self.thumbnail_path = thumbnail_dir + '/' + str(self.file_id) + '.' + self.format.lower()
        self.image.save(self.thumbnail_path)
