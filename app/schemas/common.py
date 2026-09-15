from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    message: str = "success"
    status_code: int = 200
    data: Optional[T] = None  # noqa: UP045

    @classmethod
    def sucess(cls, data: Optional[T] = None) -> "ResponseModel[T]":  # noqa: UP045
        """
        传入什么类型的data，返回的ResponseModel就自动带什么类型
        """
        return cls(data=data)

    @classmethod
    def fail(cls, code: int, message: str) -> "ResponseModel[T]":
        """失败响应，data固定为None"""
        return cls(code=code, message=message, data=None)


class PageQuery(BaseModel):
    """通用分页查询参数"""
    page: int = 1
    page_size: int = 20


class PageResult(BaseModel, Generic[T]):
    """通用分页返回结构"""
    total: int
    items: list[T]
    page: int
    page_size: int
