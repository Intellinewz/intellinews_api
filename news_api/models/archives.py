from datetime import datetime as dt
from sqlalchemy.exc import DBAPIError
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
)
from .meta import Base


class Archives(Base):
    __tablename__ = 'archives'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    description = Column(Text)
    source = Column(Text)
    date_published = Column(Text)
    url = Column(Text)
    dom_tone = Column(Text)
    image = Column(Text)
    date_created = Column(DateTime, default=dt.now())
    date_updated = Column(DateTime, default=dt.now(), onupdate=dt.now())

    def __init__(self, title=None, description=None, source=None, date_published=None, url=None, dom_tone=None, image=None):
        """ Initializes the class with the attributes of title, description,
        source, url, dominant tone, and the related image
        """
        self.title = title
        self.description = description
        self.source = source
        self.date_published = date_published
        self.url = url
        self.dom_tone = dom_tone
        self.image = image

    @classmethod
    def get_all(cls, request):
        """Method to retrieve all archives from the database
        """
        if request.dbsession is None:
            raise DBAPIError

        return request.dbsession.query(cls).all()
