# -*- coding: utf-8 -*-  # noqa: UP009
import logging
import os
import time
import traceback
from logging.handlers import RotatingFileHandler

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.user import router as user_router
from app.core.database import get_db
from app.core.exceptions import BusinessException
from app.core.result import Result

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#实例化应用
app = FastAPI()

# 1. 拦截自定义业务异常：业务代码主动raise的错误（用户不存在、权限不足等）
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """
    处理所有业务逻辑错误，直接返回我们定义的错误码和提示
    exc: 就是你raise的BusinessException对象，里面带了你传的code和message
    """
    return JSONResponse(
        status_code=200,
        content=Result.error(code=exc.code, message=exc.message).model_dump()
    )

# 2. 拦截参数校验异常：FastAPI自动校验参数失败时抛出
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理参数不合法的错误，把具体哪个字段错了、为什么错返回给前端
    exc.errors()包含所有参数错误的详细信息
    """
    # 整理错误信息，只返回字段和原因，不暴露多余细节
    error_details = []
    for err in exc.errors():
        error_details.append({
            "field": ".".join(map(str, err["loc"])),
            "reason": err["msg"]
        })

    logger.info(f"参数校验失败，请求地址：{request.url}，错误：{error_details}")
    return JSONResponse(
        status_code=200,
        content=Result.error(
            code=422,
            message="参数校验失败",
            data=error_details
        ).model_dump()
    )

# 3. 全局兜底异常：接住所有没被前面处理的未知错误（代码bug、数据库错误等）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    所有非预期错误的最后一道防线：
    1. 后端打完整错误日志，方便排查bug
    2. 前端只返回通用提示，不暴露代码细节和敏感信息
    """
    # 打完整错误堆栈，排查线上bug的关键
    logger.error("系统内部错误，请稍后再试")
    traceback.print_exc()  # 打印完整的错误堆栈
    return JSONResponse(
        status_code=200,
        content=Result.error(
            code=500,
            message="系统内部错误，请联系管理员"
        ).model_dump()
    )
@app.middleware("http")
async def log_request_middleware(request:Request, call_next):
    #请求开始：记录开始时间
    start_time = time.time()
    #把请求传给路由，拿到响应
    response = await call_next(request)
    #响应出去，计算耗时
    process_time = time.time() - start_time
    # 打访问日志：方法、路径、状态码、耗时（保留2位小数，单位秒）
    logger.info(f"{request.method} {request.url.path} | 状态码：{response.status_code} | 耗时：{process_time:.2f}s")

    # 可以把耗时放到响应头里，前端也能看到
    response.headers["X-Process_Time"] = str(process_time)
    return response

#测试数据库连接
@app.get("/test_database")
def test_database(db : Session = Depends(get_db)):  # noqa: B008
    result = db.execute(text("SELECT 1"))
    return Result.success(data={
        "status": "数据库连接成功",
        "test_result": result.scalar_one()
    })

#挂载用户模块路由
app.include_router(user_router)

log_dir = "logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# 定义日志格式：时间 | 级别 | 文件名:行号 | 日志内容
log_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#配置两个Handler

# 控制台Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# 文件Handler
file_handler = RotatingFileHandler(
    filename=os.path.join(log_dir, "app.log"),
    maxBytes=1024 *1024 *1024 *10, # 10GB
    backupCount=5,
    encoding="utf-8" 
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

Logger = logging.getLogger()
Logger.setLevel(logging.INFO)

Logger.addHandler(console_handler)
Logger.addHandler(file_handler)

Logger.propagate = False  # 防止日志重复打印