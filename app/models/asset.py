from datetime import date, datetime  # noqa: F401

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)

from app.core.database import Base


class AssetCategory(Base):
    """资产分类表"""
    __tablename__ = "asset_categories"

    id = Column(Integer, primary_key=True, comment="分类ID")
    name = Column(String(64), nullable=False, comment="分类名称")
    code = Column(String(32), nullable=False, unique=True, comment="分类编码，用于资产编号前缀")
    parent_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=True, comment="父分类ID，支持二级分类")
    sort = Column(Integer, default=0, comment="排序权重，数字越小越靠前")
    is_delete = Column(SmallInteger, default=0, comment="是否删除：0正常 1已删除")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")


class Asset(Base):
    """资产表"""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, comment="资产ID")
    asset_code = Column(String(32), nullable=False, unique=True, index=True, comment="资产编号，业务唯一键")
    name = Column(String(128), nullable=False, comment="资产名称")
    category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False, comment="所属分类ID")
    brand = Column(String(64), nullable=True, comment="品牌")
    model = Column(String(64), nullable=True, comment="型号规格")
    status = Column(String(16), nullable=False, default="idle", comment="状态：idle闲置/in_use使用中/maintenance维修中/scrapped已报废")
    purchase_date = Column(Date, nullable=True, comment="购入日期")
    purchase_price = Column(Numeric(10, 2), nullable=True, comment="购入价格")
    location = Column(String(128), nullable=True, comment="存放位置")
    current_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="当前使用人ID")
    remark = Column(Text, nullable=True, comment="备注")
    is_delete = Column(SmallInteger, default=0, comment="是否删除：0正常 1已删除")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
