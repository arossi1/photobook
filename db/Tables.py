import logging, datetime

from sqlalchemy import Column, Date, Integer, String, DateTime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


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

    def __init__(self, path : str):
        self.path = path        

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
    modified_date_time = Column(DateTime)
    hash_val = Column(String)


    def __init__(self,
                 _file : File, 
                 size : int,
                 modified_date_time : datetime.datetime,
                 hash_val : str):
        self.file = _file
        self.size = size
        self.modified_date_time = modified_date_time
        self.hash_val = hash_val

    def __repr__(self):
        return f"id: {self.id}\n" + \
               f"file: {self.file}" + \
               f"size: {self.size}" + \
               f"modified_date_time: {self.modified_date_time}" + \
               f"hash: {self.hash_val}"


################################################################################
class ImageAttributes(Base):

    __tablename__ = "image_attributes"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", backref="image_attributes")
    width = Column(Integer)
    height = Column(Integer)
    bands = Column(Integer)
    hash_val = Column(String)
    date_time = Column(DateTime)


    def __init__(self, 
                 _file : File,
                 width : int,
                 height : int,
                 bands : int,
                 hash_val : str,
                 date_time : datetime.datetime):
        self.file = _file
        self.width = width
        self.height = height
        self.bands = bands
        self.hash_val = hash_val
        self.date_time = date_time

    def __repr__(self):
        return f"id: {self.id}\n" + \
               f"file: {self.file}" + \
               f"width: {self.width}" + \
               f"height: {self.height}" + \
               f"bands: {self.bands}" + \
               f"hash_val: {self.hash_val}" + \
               f"date_time: {self.date_time}"  


################################################################################
class Db:
    Engine = None
    Session = None

    @staticmethod
    def initialize(dbPath):
        Db.Engine = create_engine('sqlite:///' + dbPath)
        Db.Session = sessionmaker(Db.Engine)

def createDatabase(dbPath):
    Db.initialize(dbPath)
    Base.metadata.create_all(Db.Engine)
