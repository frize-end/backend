# -*- coding: utf-8 -*-  # noqa: UP009
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import get_db
from app.models.user import User

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