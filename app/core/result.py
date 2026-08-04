from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

# 泛型占位符，代表任意类型的响应数据
T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """统一响应模型，外层结构固定，data类型动态指定"""
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None  # noqa: UP045

    @classmethod
    def success(cls, data=None, message="操作成功", code=200) -> "Result[T]":
        """成功响应，参数和原写法完全兼容"""
        return cls(code=code, message=message, data=data)

    @classmethod
    def error(cls, message="操作失败", code=400, data=None) -> "Result[T]":
        """失败响应，参数和原写法完全兼容"""
        return cls(code=code, message=message, data=data)