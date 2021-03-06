import logging

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
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

    @classmethod
    def find_next_image_id(cls, session, image_id):
        try:
            res = session.query(cls).filter(cls.id > image_id).order_by(cls.id.asc()).first()
        except NoResultFound:
            return None

        return res.id

    @classmethod
    def find_prev_image_id(cls, session, image_id):
        try:
            res = session.query(cls).filter(cls.id < image_id).order_by(cls.id.desc()).first()
        except NoResultFound:
            return None

        return res.id

    def __init__(self, file_id, path):
        self.logger = logging.getLogger('MediaLibraryManager')

        self.path = path
        self.image = PILImage.open(path)
        self.file_id = file_id
        self.format = self.image.format
        self.height = self.image.height
        self.width = self.image.width
        self.thumbnail_path = None

    def create_thumbnail(self, thumbnail_dir):

        if not thumbnail_dir:
            thumbnail_dir = 'thumbnails'

        image_orientation = None
        try:
            image_orientation = self.image._getexif().get(274, None)
        except AttributeError:
            pass

        try:
            self.image.thumbnail(THUMBNAIL_MAX_SIZE)
        except OSError:
            self.logger.error("Could not create thumbnail for image '{}'".format(self.path))
            return

        if image_orientation == 3:
            self.image = self.image.transpose(PILImage.ROTATE_180)
        elif image_orientation == 6:
            self.image = self.image.transpose(PILImage.ROTATE_270)
        elif image_orientation == 8:
            self.image = self.image.transpose(PILImage.ROTATE_90)

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
