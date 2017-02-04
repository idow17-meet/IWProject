from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from database_setup import *
from datetime import datetime

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Populating the database:

nathan = ScoreInfo(userid = '666666666666666666', score = 8, name="Nathan Nathan")
ido = ScoreInfo(userid = '103891305576825217486', score = 3, name="Ido Wiernik")
ron = ScoreInfo(userid = '312312312515125215811', score = 1, name="Ron Miles")

session.query(ScoreInfo).delete()

session.add(nathan)
session.add(ido)
session.add(ron)
session.commit()