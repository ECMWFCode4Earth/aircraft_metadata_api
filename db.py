
from sqlalchemy import create_engine, ForeignKey, CheckConstraint, Column, DateTime, Integer, String,Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime



engine = create_engine('sqlite:///database/database.db', echo=True)
Base = declarative_base(engine)
session_factory = sessionmaker(bind=engine)

class Planetype(Base):
    __tablename__ = "Planetype"
    id = Column(Integer, primary_key=True)
    amdarid = Column(String)
    flightid = Column(String)
    planetype = Column(String)
    time = Column(String)
    dep = Column(String)
    arr = Column(String)
    datasource = Column(String)

    def serialize(self):
        return {
            'amdarid': self.amdarid,
            'fligthid': self.flightid,
            'planetype': self.planetype,
            'time': self.time,
            'dep' : self.dep,
            'arr' : self.arr,
            'datasource': self.datasource
        }

class Timezone(Base):
    __tablename__ = "Timezone"
    id = Column(Integer, primary_key=True)
    timezone = Column(String)
    utcdiff = Column(String)

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
    international = Column(Integer,default=0)
    
    def serialize(self):
        return{
            'icao': self.icao,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
        }

class Airline(Base):
    __tablename__ = "Airline"
    id = Column(Integer, primary_key=True)
    iata = Column(String(2))
    icao = Column(String(3))
    name = Column(String(50))

class Noroute(Base):
    __tablename__ = "noroute"
    id = Column(Integer, primary_key=True)
    arr = Column(String(4))
    dep = Column(String(4))
    



def reinit():
    Base.metadata.drop_all()
    Base.metadata.create_all()

def recreate_table(table_name):
    session = session_factory()
    session.execute(f"drop table {table_name}")
    session.commit()
    Base.metadata.tables[f"{table_name}"].create(bind = engine)

def create_table(table_name):
    Base.metadata.tables[f"{table_name}"].create(bind = engine)