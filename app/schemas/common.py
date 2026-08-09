from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

#定义一个泛型占位符 T
T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    message: str = "success"
    status_code: int = 200
    data: Optional[T] = None  # noqa: UP045


    @classmethod
    def sucess(cls, data: Optional[T]=None) -> "ResponseModel[T]":  # noqa: UP045
           """
        传入什么类型的data，返回的ResponseModel就自动带什么类型
        用法和你之前的Result.success()完全一样
        """
           return cls(data=data)


    @classmethod
    def fail(cls,code:int,message:str)  -> "ResponseModel[T]":
          """失败响应，data固定为None"""
          return cls(code=code,message=message,data=None)

class PageQuery(BaseModel):
    page: int = 1
    page_size: int = 20

class PageResult(Generic[T]):
    total: int
    items: list[T]
    page: int
    page_size: int