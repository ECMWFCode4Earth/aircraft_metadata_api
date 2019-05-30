
from sqlalchemy import create_engine, ForeignKey, CheckConstraint, Column, DateTime, Integer, String,Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime



engine = create_engine('sqlite:///database/database.db', echo=True)
Base = declarative_base(engine)
session_factory = sessionmaker(bind=engine)

class Planetype(Base):
    __tablename__ = "Planetype"
    amdarid = Column(String, primary_key=True)
    flightid = Column(String)
    planetype = Column(String)
    deptime = Column(Integer)
    arrtime = Column(Integer)
    dep = Column(String)
    depcount = Column(Integer,default=0)
    arr = Column(String)
    arrcount = Column(Integer, default=0)

    def serialize(self):
        return {
            'amdarid': self.amdarid,
            'fligthid': self.flightid,
            'planetype': self.planetype,
            'deptime': self.deptime,
            'arrtime': self.arrtime,
            'dep' : self.dep,
            'depcount': self.depcount,
            'arr' : self.arr,
            'arrcount' : self.arrcount,
        }


class Route(Base):
    __tablename__ = "Route"
    id = Column(Integer, primary_key=True)
    flightid = Column(String(20))
    dep = Column(String(5), nullable=False)
    arr = Column(String(5), nullable=False)
    
    def serialize(self):
        return{
            'flightid': self.flightid,
            'dep': self.dep,
            'arr': self.arr,
        }

class Airport(Base):
    __tablename__ = "Airport"
    iata = Column(String(5), primary_key=True)
    icao = Column(String(5))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    
    def serialize(self):
        return{
            'icao': self.icao,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
        }


def reinit():
    Base.metadata.drop_all()
    Base.metadata.create_all()