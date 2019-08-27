from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def create_database(db_name):

    engine = create_engine('sqlite:///{}.sqlite'.format(db_name))
    sessionm = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    return sessionm


class SharedSql:

    def __init__(self):
        self.id = None

    def add_to_db(self, session):

        if not self.id:
            session.add(self)
            session.commit()

    def update_in_db(self, session):

        if self.id:
            session.add(self)
            session.commit()
