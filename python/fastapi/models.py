import uuid
from sqlalchemy import Column, String, INT, BLOB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pyeup(Base):
    __tablename__ = 'pyeup'
    id = Column(String(120), primary_key=True)
    year = Column(INT, unique=False, nullable=False)
    subject = Column(String(255), unique=False, nullable=False)
    count = Column(INT, unique=False, nullable=False)
    percentage = Column(INT, unique=False, nullable=False)

class PyeupApi(Base):
    __tablename__ = 'pyeupapi'
    id = Column(String(120), primary_key=True)
    subject = Column(String(255), unique=False, nullable=False)
    count = Column(INT, unique=False, nullable=False)

class GraphImg(Base):
    __tablename__ = 'graphimg'
    subject = Column(String(45), primary_key=True)
    image = Column(BLOB)

