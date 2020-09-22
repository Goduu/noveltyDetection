from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
from sqlalchemy.orm import scoped_session


engine = create_engine('sqlite:///database.db')
session_factory  = sessionmaker(bind=engine)
session = scoped_session(session_factory )
