from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

# ========== 资产状态枚举 ==========

class AssetStatus(str, Enum):
    """资产状态枚举，用于接口参数校验"""
    idle = "idle"           # 闲置
    in_use = "in_use"       # 使用中
    maintenance = "maintenance"  # 维修中
    scrapped = "scrapped"   # 已报废


# ========== 分类 DTO ==========

class CategoryCreate(BaseModel):
    """创建分类入参"""
    name: str = Field(..., max_length=64, description="分类名称")
    code: str = Field(..., max_length=32, description="分类编码，用于资产编号前缀")
    parent_id: int | None = Field(None, description="父分类ID，不传为顶级分类")
    sort: int = Field(0, description="排序权重")


class CategoryUpdate(BaseModel):
    """更新分类入参，所有字段可选"""
    name: str | None = Field(None, max_length=64, description="分类名称")
    parent_id: int | None = Field(None, description="父分类ID")
    sort: int | None = Field(None, description="排序权重")


class CategoryResponse(BaseModel):
    """分类返回结构"""
    id: int
    name: str
    code: str
    parent_id: int | None
    sort: int
    create_time: datetime

    class Config:
        from_attributes = True


# ========== 资产 DTO ==========

class AssetCreate(BaseModel):
    """新增资产入参（资产编号由系统自动生成，不需要传）"""
    name: str = Field(..., max_length=128, description="资产名称")
    category_id: int = Field(..., description="所属分类ID")
    brand: str | None = Field(None, max_length=64, description="品牌")
    model: str | None = Field(None, max_length=64, description="型号规格")
    purchase_date: date | None = Field(None, description="购入日期")
    purchase_price: Decimal | None = Field(None, ge=0, description="购入价格")
    location: str | None = Field(None, max_length=128, description="存放位置")
    current_user_id: int | None = Field(None, description="当前使用人ID")
    remark: str | None = Field(None, description="备注")


class AssetUpdate(BaseModel):
    """更新资产入参，所有字段可选"""
    name: str | None = Field(None, max_length=128, description="资产名称")
    category_id: int | None = Field(None, description="所属分类ID")
    brand: str | None = Field(None, max_length=64, description="品牌")
    model: str | None = Field(None, max_length=64, description="型号规格")
    status: AssetStatus | None = Field(None, description="资产状态")
    purchase_date: date | None = Field(None, description="购入日期")
    purchase_price: Decimal | None = Field(None, ge=0, description="购入价格")
    location: str | None = Field(None, max_length=128, description="存放位置")
    current_user_id: int | None = Field(None, description="当前使用人ID")
    remark: str | None = Field(None, description="备注")