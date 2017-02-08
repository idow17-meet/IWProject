from database_setup import *
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()


# This script is used in conjunction with -i to edit the database if needed