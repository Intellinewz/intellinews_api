from datetime import datetime as dt
from sqlalchemy.exc import DBAPIError
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    JSON,
)
from .meta import Base


class Archives(Base):
    __tablename__ = 'archives'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    description = Column(Text)
    source = Column(Text)
    date_published = Column(Text)
    url = Column(Text)
    image = Column(Text)
    dom_tone = Column(Text)
    vocab_score = Column(Integer)
    num_words = Column(Integer)
    sentence_breakdown = Column(JSON)
    date_created = Column(DateTime, default=dt.now())
    date_updated = Column(DateTime, default=dt.now(), onupdate=dt.now())

    def __init__(self, title=None, description=None, source=None, date_published=None, url=None, image=None, dom_tone=None, vocab_score=None, num_words=None, sentence_breakdown=None):
        """ Initializes the feed with attributes of title, description, source,
        date published, url to the article, dominant tone, and related image
        """
        self.title = title
        self.description = description
        self.source = source
        self.date_published = date_published
        self.url = url
        self.image = image
        self.dom_tone = dom_tone
        self.vocab_score = vocab_score
        self.num_words = num_words
        self.sentence_breakdown = sentence_breakdown

    @classmethod
    def get_all(cls, request):
        """Method to retrieve all archives from the database
        """
        if request.dbsession is None:
            raise DBAPIError

        return request.dbsession.query(cls).all()
