from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql

import os

Base = declarative_base()

class ScoreInfo(Base):
	__tablename__ = 'scores'
	id = Column(Integer, primary_key=True)
	userid = Column(String)
	score = Column(Integer)
	name = Column(String)

#engine = create_engine('sqlite:///project.db')
# try:
# 	a = os.system("ping google.com")
# 	if (a == 512):
# 		raise "eeerororororor"
# 	engine = create_engine(os.environ["DATABASE_URL"])
# except:
# 	engine = create_engine("sqlite:///project.db")
engine = create_engine(os.environ["DATABASE_URL"])
Base.metadata.create_all(engine)
