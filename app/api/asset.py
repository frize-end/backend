"""
资产模块路由
- 分类管理：管理员可增删改，登录用户可查看
- 资产管理：管理员可增删改，登录用户可查看
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core import (
    BusinessException,
    Result,
    get_current_admin,
    get_current_user,
    get_db,
)
from app.crud import crud_asset
from app.models.user import User
from app.schemas.asset import (
    AssetCreate,
    AssetResponse,
    AssetStatus,
    AssetUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.schemas.common import PageResult

router = APIRouter(prefix="/assets", tags=["资产管理"])


# ============================================================
# 资产分类接口
# ============================================================

@router.post("/categories", response_model=Result[CategoryResponse], summary="创建分类")
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    """管理员创建资产分类"""
    # 校验编码唯一
    if crud_asset.get_category_by_code(db, data.code):
        raise BusinessException(code=409, message="分类编码已存在")
    # 校验父分类
    if data.parent_id and not crud_asset.get_category(db, data.parent_id):
        raise BusinessException(code=404, message="父分类不存在")

    category = crud_asset.create_category(db, data)
    return Result.success(data=CategoryResponse.model_validate(category))


@router.get("/categories", response_model=Result[list[CategoryResponse]], summary="分类列表")
def list_categories(
    db: Session = Depends(get_db),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
):
    """查询所有分类（平铺列表）"""
    categories = crud_asset.list_categories(db)
    return Result.success(data=[CategoryResponse.model_validate(c) for c in categories])


@router.patch("/categories/{category_id}", response_model=Result[CategoryResponse], summary="更新分类")
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    """管理员更新分类信息"""
    category = crud_asset.get_category(db, category_id)
    if not category:
        raise BusinessException(code=404, message="分类不存在")

    # 不能把自己设为自己的父分类
    if data.parent_id == category_id:
        raise BusinessException(code=400, message="父分类不能是自己")
    if data.parent_id and not crud_asset.get_category(db, data.parent_id):
        raise BusinessException(code=404, message="父分类不存在")

    category = crud_asset.update_category(db, category, data)
    return Result.success(data=CategoryResponse.model_validate(category))


@router.delete("/categories/{category_id}", response_model=Result[None], summary="删除分类")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    """管理员删除分类（分类下有资产时不允许删除）"""
    category = crud_asset.get_category(db, category_id)
    if not category:
        raise BusinessException(code=404, message="分类不存在")

    # 检查分类下是否还有资产
    asset_count = crud_asset.count_assets_in_category(db, category_id)
    if asset_count > 0:
        raise BusinessException(code=409, message=f"该分类下还有 {asset_count} 项资产，无法删除")

    crud_asset.delete_category(db, category)
    return Result.success(message="删除成功")


# ============================================================
# 资产接口
# ============================================================

def _generate_asset_code(db: Session, category_id: int) -> str:
    """
    生成资产编号：{分类编码}-{年月日}-{3位流水号}
    例：IT-20260810-001
    """
    category = crud_asset.get_category(db, category_id)
    if not category:
        raise BusinessException(code=404, message="分类不存在")

    date_str = datetime.now().strftime("%Y%m%d")  # noqa: DTZ005
    seq = crud_asset.get_max_asset_seq(db, category.code, date_str)
    return f"{category.code}-{date_str}-{seq + 1:03d}"


@router.post("", response_model=Result[AssetResponse], summary="新增资产")
def create_asset(
    data: AssetCreate,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    """管理员录入资产，资产编号自动生成"""
    # 校验分类存在
    if not crud_asset.get_category(db, data.category_id):
        raise BusinessException(code=404, message="分类不存在")

    # 校验使用人存在
    if data.current_user_id is not None:
        user_exists = db.query(User).filter(
            User.id == data.current_user_id, User.is_delete == 0
        ).first()
        if not user_exists:
            raise BusinessException(code=404, message="指定的使用人不存在")

    # 自动生成资产编号
    asset_code = _generate_asset_code(db, data.category_id)
    asset = crud_asset.create_asset(db, data, asset_code)
    return Result.success(data=AssetResponse.model_validate(asset))


@router.get("", response_model=Result[PageResult[AssetResponse]], summary="资产列表（分页）")
def list_assets(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数，最大100"),
    category_id: int | None = Query(None, description="按分类筛选"),
    status: AssetStatus | None = Query(None, description="按状态筛选"),  # noqa: B008
    keyword: str | None = Query(None, description="按资产名称模糊搜索"),
    db: Session = Depends(get_db),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
):
    """分页查询资产列表，支持分类、状态、关键词筛选"""
    status_value = status.value if status else None
    total, items = crud_asset.list_assets(
        db, page=page, page_size=page_size,
        category_id=category_id, status=status_value, keyword=keyword,
    )
    return Result.success(data=PageResult(
        total=total,
        items=[AssetResponse.model_validate(a) for a in items],
        page=page,
        page_size=page_size,
    ))


@router.get("/{asset_id}", response_model=Result[AssetResponse], summary="资产详情")
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
):
    """根据ID查询资产详情"""
    asset = crud_asset.get_asset(db, asset_id)
    if not asset:
        raise BusinessException(code=404, message="资产不存在")
    return Result.success(data=AssetResponse.model_validate(asset))


@router.patch("/{asset_id}", response_model=Result[AssetResponse], summary="更新资产")
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    """管理员更新资产信息"""
    asset = crud_asset.get_asset(db, asset_id)
    if not asset:
        raise BusinessException(code=404, message="资产不存在")

    # 如果改了分类，校验新分类存在
    if data.category_id and not crud_asset.get_category(db, data.category_id):
        raise BusinessException(code=404, message="分类不存在")

    # 如果改了使用人，校验用户存在
    if data.current_user_id is not None:
        user_exists = db.query(User).filter(
            User.id == data.current_user_id, User.is_delete == 0
        ).first()
        if not user_exists:
            raise BusinessException(code=404, message="指定的使用人不存在")

    asset = crud_asset.update_asset(db, asset, data)
    return Result.success(data=AssetResponse.model_validate(asset))


@router.delete("/{asset_id}", response_model=Result[None], summary="删除资产")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    """管理员删除资产（逻辑删除）"""
    asset = crud_asset.get_asset(db, asset_id)
    if not asset:
        raise BusinessException(code=404, message="资产不存在")
    crud_asset.delete_asset(db, asset)
    return Result.success(message="删除成功")
