from datetime import datetime

from sqlalchemy import Column, Datetime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primarykey=True, index=True)
    username = Column(String(10),nullable=False,index=True)
    password = Column(String(20),nullable=False)
    datetime = Column(Datetime,default=datetime.now,comment="创建时间")