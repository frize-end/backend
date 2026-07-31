from datetime import datetime

from sqlalchemy import Column, Datetime, Integer, String

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primarykey=True)
    username = Column(String(32),nullable=False,index=True)
    password = Column(String(128),nullable=False)
    creat_time = Column(Datetime,default=datetime.now,comment="创建时间")