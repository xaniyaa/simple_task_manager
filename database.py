from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import VARCHAR
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import MetaData

engine = create_engine('sqlite:///tasks.db', echo=True)
Base = declarative_base(bind=engine)
metadata = MetaData(engine)

class Tasks(Base):
    __tablename__ = 'tasks' 
    id = Column('id', Integer, primary_key=True)
    name = Column('name', VARCHAR(255), nullable=False)
    description = Column('description', VARCHAR(255), nullable=True)
    active = Column('active', Boolean, nullable=False)
    category_id = Column('category_id', Integer, ForeignKey('categories.id'), nullable=True)
    Categories = relationship('Categories')


class Categories(Base):
    __tablename__ = 'categories' 
    id = Column('id', Integer, primary_key=True)
    name = Column('name', VARCHAR(255), nullable=False)

Base.metadata.create_all(engine)

