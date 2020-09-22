import sqlalchemy as db
from sqlalchemy import Column,Sequence
from db_conexion import engine
from sqlalchemy.ext.declarative import declarative_base

# session = Session()

Base = declarative_base()

class Consumption(Base):
    

    __tablename__ = 'Consumption'
    id = db.Column(db.Integer, Sequence('consumption_id_seq'),primary_key =True)
    client_id = db.Column(db.String)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    value = db.Column(db.Float)
    v1 = db.Column(db.Float)
    dif1 = db.Column(db.Float)
    v2 = db.Column(db.Float)
    dif2 = db.Column(db.Float)
    v3 = db.Column(db.Float)
    dif3 = db.Column(db.Float)
    v4 = db.Column(db.Float)
    dif4 = db.Column(db.Float)
    movAvg = db.Column(db.Float)
    movStd = db.Column(db.Float)
    integrated = db.Column(db.Boolean)

    def __repr__(self):
        return "<Consumption(client_id='%s , value_id=%d')>" % (self.client_id,self.value)    
    
Consumption.__table__.create(bind=engine, checkfirst=True)