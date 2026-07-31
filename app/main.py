# -*- coding: utf-8 -*-  # noqa: UP009
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import get_db

#实例化应用
app = FastAPI()


settings = Settings()
print(settings.user, settings.user_host, settings.user_password)


@app.get("/test_database")
def test_database(db : Session = Depends(get_db)):  # noqa: B008
    result = db.execute(text("SELECT 1"))
    return {
    "status": "数据库连接成功",
    "test_result": result.scalar_one()
}