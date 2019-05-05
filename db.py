
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
    planetype = Column(String(20))
    deptime = Column(DateTime)
    arrtime = Column(DateTime)
    dep = Column(String(4))
    arr = Column(String(4))
    deplat = Column(Float)
    deplong = Column(Float)
    arrlat = Column(Float)
    arrlong = Column(Float)

    def serialize(self):
        return {
            'amdarid': self.amdarid,
            'planetype': self.planetype,
            'deptime': self.deptime,
            'arrtime': self.arrtime,
            'dep': self.dep,
            'arr': self.arr,
            'deplat': self.deplat,
            'deplong': self.deplong,
            'arrlat': self.arrlat,
            'arrlong': self.arrlong
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