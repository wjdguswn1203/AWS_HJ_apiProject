import uuid
from sqlalchemy import Column, String, INT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pyeup(Base):
    __tablename__ = 'pyeup'
    id = Column(String(120), primary_key=True)
    year = Column(INT, unique=False, nullable=False)
    subject = Column(String(255), unique=False, nullable=False)
    count = Column(INT, unique=False, nullable=False)
    percentage = Column(INT, unique=False, nullable=False)

