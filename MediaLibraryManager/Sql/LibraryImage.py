import logging

from sqlalchemy import Column, Integer, String
from PIL import Image

from MediaLibraryManager.Sql.Main import Base


class LibraryImage(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer)
    format = Column(String)
    height = Column(Integer)
    width = Column(Integer)

    def __init__(self, file_id, path):
        self.logger = logging.getLogger('MediaLibraryManager')

        self.image = Image.open(path)
        self.file_id = file_id
        self.format = self.image.format
        self.height = self.image.height
        self.width = self.image.width

    def add_to_db(self, session):

        if not self.id:
            session.add(self)
            session.commit()
