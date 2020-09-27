from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
from sqlalchemy.orm import scoped_session
import logging
import sys 

logging.basicConfig(filename="app.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

engine = create_engine('sqlite:///database.db')
engine_clustering = create_engine('sqlite:///databaseClustering.db')

session_factory  = sessionmaker(bind=engine)
session = scoped_session(session_factory )
