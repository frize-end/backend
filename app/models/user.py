from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, SmallInteger, String

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, comment="用户id")
    username = Column(String(32),nullable=False,index=True, comment="用户名")
    password = Column(String(128),nullable=False, comment="密码")
    create_time = Column(DateTime,default=datetime.now,comment="创建时间")
    is_delete = Column(SmallInteger,default=0,comment="是否删除")
    phone = Column(String(11),nullable=False,comment="手机号")