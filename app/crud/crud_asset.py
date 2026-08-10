"""
资产模块数据访问层（CRUD）
只负责和数据库打交道，不写业务逻辑，不抛业务异常
业务校验和异常由 API 层负责
"""
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetCategory
from app.schemas.asset import AssetCreate, AssetUpdate, CategoryCreate, CategoryUpdate


# ============================================================
# 资产分类 CRUD
# ============================================================

def create_category(db: Session, data: CategoryCreate) -> AssetCategory:
    """创建分类"""
    category = AssetCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> AssetCategory | None:
    """根据ID查询未删除的分类"""
    return db.query(AssetCategory).filter(
        AssetCategory.id == category_id,
        AssetCategory.is_delete == 0,
    ).first()


def get_category_by_code(db: Session, code: str) -> AssetCategory | None:
    """根据编码查询未删除的分类"""
    return db.query(AssetCategory).filter(
        AssetCategory.code == code,
        AssetCategory.is_delete == 0,
    ).first()


def list_categories(db: Session) -> list[AssetCategory]:
    """查询所有未删除的分类，按排序权重和ID排序"""
    return db.query(AssetCategory).filter(
        AssetCategory.is_delete == 0,
    ).order_by(AssetCategory.sort, AssetCategory.id).all()


def count_assets_in_category(db: Session, category_id: int) -> int:
    """统计分类下未删除的资产数量"""
    return db.query(Asset).filter(
        Asset.category_id == category_id,
        Asset.is_delete == 0,
    ).count()


def update_category(db: Session, category: AssetCategory, data: CategoryUpdate) -> AssetCategory:
    """更新分类信息"""
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: AssetCategory) -> None:
    """逻辑删除分类"""
    category.is_delete = 1
    db.commit()


# ============================================================
# 资产 CRUD
# ============================================================

def create_asset(db: Session, data: AssetCreate, asset_code: str) -> Asset:
    """创建资产，asset_code 由业务层生成后传入"""
    asset = Asset(asset_code=asset_code, **data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_asset(db: Session, asset_id: int) -> Asset | None:
    """根据ID查询未删除的资产"""
    return db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.is_delete == 0,
    ).first()


def list_assets(
    db: Session,
    page: int,
    page_size: int,
    category_id: int | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> tuple[int, list[Asset]]:
    """
    分页查询资产
    返回 (总条数, 当前页数据列表)
    """
    query = db.query(Asset).filter(Asset.is_delete == 0)

    if category_id is not None:
        query = query.filter(Asset.category_id == category_id)
    if status is not None:
        query = query.filter(Asset.status == status)
    if keyword:
        query = query.filter(Asset.name.like(f"%{keyword}%"))

    total = query.count()
    items = (
        query.order_by(Asset.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def update_asset(db: Session, asset: Asset, data: AssetUpdate) -> Asset:
    """更新资产信息"""
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(asset, key, value)
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset: Asset) -> None:
    """逻辑删除资产"""
    asset.is_delete = 1
    db.commit()


def get_max_asset_seq(db: Session, category_code: str, date_str: str) -> int:
    """
    查询当天该分类下资产编号的最大流水号
    用于生成下一个资产编号
    编号格式：{category_code}-{date_str}-{seq:03d}
    """
    prefix = f"{category_code}-{date_str}-"
    latest = (
        db.query(Asset)
        .filter(Asset.asset_code.like(f"{prefix}%"), Asset.is_delete == 0)
        .order_by(Asset.asset_code.desc())
        .first()
    )
    if not latest:
        return 0
    try:
        seq_str = latest.asset_code.rsplit("-", maxsplit=1)[-1]
        return int(seq_str)
    except (ValueError, IndexError):
        return 0
