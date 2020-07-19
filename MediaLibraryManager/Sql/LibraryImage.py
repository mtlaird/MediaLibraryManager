import logging

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from PIL import Image as PILImage

from MediaLibraryManager.Sql.Main import Base, BaseMixin

THUMBNAIL_MAX_SIZE = (150, 150)


class Image(BaseMixin, Base):

    file_id = Column(Integer, ForeignKey('file.id'))
    format = Column(String)
    height = Column(Integer)
    width = Column(Integer)
    thumbnail_path = Column(String)

    file_info = relationship('File')

    def __init__(self, file_id, path):
        self.logger = logging.getLogger('MediaLibraryManager')

        self.image = PILImage.open(path)
        self.file_id = file_id
        self.format = self.image.format
        self.height = self.image.height
        self.width = self.image.width
        self.thumbnail_path = None

    def create_thumbnail(self, thumbnail_dir):

        if not thumbnail_dir:
            thumbnail_dir = 'thumbnails'

        self.image.thumbnail(THUMBNAIL_MAX_SIZE)
        self.thumbnail_path = thumbnail_dir + '/' + str(self.file_id) + '.' + self.format.lower()
        self.image.save(self.thumbnail_path)


# TODO: Implement photo class / table based on EXIF tags
# class LibraryPhoto(Base):
#     __tablename__ = 'photos'
#
#     id = Column(Integer, primary_key=True)
#     image_id = Column(Integer, ForeignKey('images.id'))
#
#     image_info = relationship('LibraryImage')
#
#     def __init__(self, image):
#         self.image = image
