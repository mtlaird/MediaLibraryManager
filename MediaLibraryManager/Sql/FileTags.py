from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from MediaLibraryManager.Sql.Main import Base


class FileTag(Base):
    __tablename__ = 'files_tags'

    file_id = Column(Integer, ForeignKey('files.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)

    relationship('Tag')

    def __init__(self, **kwargs):

        self.file_id = kwargs.pop('file_id')
        self.tag_id = kwargs.pop('tag_id')

    @classmethod
    def get_tags_by_file_id(cls, session, file_id):
        return session.query(FileTag).filter(FileTag.file_id == file_id).all()


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    value = Column(String)

    def __init__(self, **kwargs):

        self.type = kwargs.pop('type')
        self.value = kwargs.pop('value')

    @classmethod
    def get_or_create(cls, session, tag_type, tag_value):
        try:
            return session.query(Tag).filter(Tag.type == tag_type).filter(Tag.value == tag_value).one()
        except NoResultFound:
            new_tag = Tag(type=tag_type, value=tag_value)
            session.add(new_tag)
            session.commit()
            return new_tag

