# -*- coding: utf-8 -*-  # noqa: UP009
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.user import router as user_router
from app.core.config import Settings
from app.core.database import get_db
from app.core.exceptions import BusinessException

#实例化应用
app = FastAPI()

# 1. 拦截自定义业务异常
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None
        }
    )

# 2. 拦截参数校验异常
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        content={
            "code": 422,
            "message": "参数格式错误",
            "data": None
        }
    )

# 3. 全局兜底异常
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={
            "code": 500,
            "message": "系统内部错误，请联系管理员",
            "data": None
        }
    )
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

#挂载用户模块路由
app.include_router(user_router)