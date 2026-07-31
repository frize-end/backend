# -*- coding: utf-8 -*-  # noqa: UP009
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import get_db
from app.models.user import User
from app.schemas import UserUpdateDTO

#实例化应用
app = FastAPI()


settings = Settings()
print(settings.user, settings.user_host, settings.user_password)
#测试数据库连接
@app.get("/test_database")
def test_database(db : Session = Depends(get_db)):  # noqa: B008
    result = db.execute(text("SELECT 1"))
    return {
    "status": "数据库连接成功",
    "test_result": result.scalar_one()
}

#新增用户
@app.post("/add_user")
def add_user(username: str, password: str, db : Session = Depends(get_db)):  # noqa: B008
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id":user.id,
        "username":user.username,
        "create_time":user.create_time
    }
#查询用户
@app.get("/get_user/{id}")
def get_user(id: int , db : Session = Depends(get_db)):  # noqa: B008
    user = db.quary(User).filter(User.id == id).first()
    if not User:
        raise ValueError("用户不存在")
    return {
        "id":user.id,
        "username":user.username,
        "create_time":user.create_time
    }

#更改用户信息
@app.patch("/user/{user_id}")
def update_user(user_id:int,update_data: UserUpdateDTO,db: Session = Depends(get_db)):  # noqa: B008
    user = db.query(User).filter(User.id == user_id).first()
    #检测用户是否存在
    if not user :
        raise ValueError("用户不存在")

    date_dict = update_data.model_dump(exclude_unset=True)

    for key,value in date_dict.items():
        setattr(user,key,value)
    db.commit()
    db.refresh(user)
    return user