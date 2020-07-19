from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def create_database(db_name):

    engine = create_engine('sqlite:///{}.sqlite'.format(db_name), connect_args={'check_same_thread': False})
    sessionm = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    return sessionm


class BaseMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)

    def add_to_db(self, session, commit=True):

        self.custom_pre_add(session)

        if not self.id:
            try:
                session.add(self)
            except Exception:
                raise
            if commit:
                session.commit()

        self.custom_post_add(session)

        return True

    def update_in_db(self, session, commit=True):

        self.custom_update(session)

        if self in session and self.id and self in session.dirty:
            if commit:
                session.commit()
            return True
        return False

    @classmethod
    def select_all(cls, session):

        return session.query(cls).all()

    @classmethod
    def select_some(cls, session, **kwargs):

        return session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def select_one(cls, session, **kwargs):

        return session.query(cls).filter_by(**kwargs).first()

    def custom_pre_add(self, session):
        pass

    def custom_post_add(self, session):
        pass

    def custom_update(self, session):
        pass
