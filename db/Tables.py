import logging

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

Base = declarative_base()
engine = None


################################################################################
class RootPath(Base):

    __tablename__ = "root_path"

    id = Column(Integer, primary_key=True)
    windows = Column(String)
    linux = Column(String)

    def __init__(self, windows : str, linux : str):
        self.windows = windows
        self.linux = linux

    def __repr__(self):
        return f"id: {self.id}\n" + \
               f"windows: {self.windows}\n" + \
               f"linux: {self.linux}"


################################################################################
class File(Base):

    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    size = Column(Integer)

    def __init__(self, path : str, size : int):
        self.path = path
        self.size = size

    def __repr__(self):
        return f"id: {self.id}\n" + \
               f"path: {self.path}"


################################################################################
class FileAttributes(Base):

    __tablename__ = "file_attributes"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", backref="file_attributes")
    size = Column(Integer)

    def __init__(self, _file : File, size : int):
        self.file = _file
        self.size = size

    def __repr__(self):
        return f"id: {self.id}\n" + \
               f"file: {self.file}" + \
               f"size: {self.size}"

def createDatabase(dbPath):
    engine = create_engine('sqlite:///' + dbPath)
    Base.metadata.create_all(engine)
