from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql

import os
import psycopg2
import urlparse

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

Base = declarative_base()

class ScoreInfo(Base):
	__tablename__ = 'scores'
	id = Column(Integer, primary_key=True)
	userid = Column(String)
	score = Column(Integer)
	name = Column(String)

#engine = create_engine('sqlite:///project.db')
engine = create_engine(os.environ["DATABASE_URL"])
# NOTE REPLACE THE LONG LINK WITH A [URL] VARIABLE LATER
Base.metadata.create_all(engine)