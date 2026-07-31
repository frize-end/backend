from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, comment="用户id")
    username = Column(String(32),nullable=False,index=True, comment="用户名")
    password = Column(String(128),nullable=False, comment="密码")
    creat_time = Column(DateTime,default=datetime.now,comment="创建时间")