from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import (
    BusinessException,
    Result,
    create_access_token,
    get_current_admin,
    get_current_user,
    get_db,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreateDTO, UserLoginDTO, UserResponseDTO, UserUpdateDTO

router = APIRouter(prefix="/user", tags=["用户管理"])

# ============================================
# 管理员接口（需要管理员角色）
# ============================================


# 新增用户
@router.post("", response_model=Result[UserResponseDTO], summary="管理员创建用户")
def add_user(
    user_data: UserCreateDTO,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    # 检测用户名是否已存在
    exists = db.query(User).filter(User.username == user_data.username, User.is_delete == 0).first()
    if exists:
        raise BusinessException(code=409, message="用户已存在")

    # 创建新用户
    new_user = User(
        username=user_data.username,
        password=hash_password(user_data.password),
        phone=user_data.phone,
        role=user_data.role,
        is_delete=0,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return Result.success(data=UserResponseDTO.model_validate(new_user))


# 查询单个用户
@router.get("/{user_id}", response_model=Result[UserResponseDTO], summary="查询用户详情")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        raise BusinessException(code=404, message="用户不存在")
    return Result.success(data=UserResponseDTO.model_validate(user))


# 修改用户信息
@router.patch("/{user_id}", response_model=Result[UserResponseDTO], summary="管理员修改用户")
def update_user(
    user_id: int,
    update_data: UserUpdateDTO,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        raise BusinessException(code=404, message="用户不存在")

    data_dict = update_data.model_dump(exclude_unset=True)

    if "password" in data_dict:
        data_dict["password"] = hash_password(data_dict["password"])

    for key, value in data_dict.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return Result.success(data=UserResponseDTO.model_validate(user))


# 删除用户（逻辑删除）
@router.delete("/{user_id}", response_model=Result[None], summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        raise BusinessException(code=404, message="用户不存在")
    user.is_delete = 1
    db.commit()
    return Result.success(message="删除成功")


# 恢复已删除用户
@router.put("/{user_id}/restore", response_model=Result[UserResponseDTO], summary="恢复用户")
def restore_user(
    user_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    admin: User = Depends(get_current_admin),  # noqa: B008
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(code=404, message="用户不存在")
    if user.is_delete == 0:
        raise BusinessException(code=409, message="用户未被删除，无需恢复")
    user.is_delete = 0
    db.commit()
    return Result.success(data=UserResponseDTO.model_validate(user))


# 用户登录（公开接口，不需要认证）
@router.post("/login", summary="用户登录", response_model=Result[dict])
def login(login_data: UserLoginDTO, db: Session = Depends(get_db)):  # noqa: B008
    user = db.query(User).filter(User.username == login_data.username, User.is_delete == 0).first()
    if not user or not verify_password(login_data.password, user.password):
        raise BusinessException(code=401, message="用户名或密码错误")

    access_token = create_access_token(data={"sub": str(user.id)})

    return Result.success(
        data={"access_token": access_token, "token_type": "bearer"}
    )


# ============================================
# 当前用户接口（登录即可访问）
# ============================================


@router.get("/me", response_model=Result[UserResponseDTO], summary="获取我的信息")
def get_my_info(current_user: User = Depends(get_current_user)):  # noqa: B008
    return Result.success(data=UserResponseDTO.model_validate(current_user))


@router.patch("/me", response_model=Result[UserResponseDTO], summary="修改我的信息")
def update_my_info(
    update_data: UserUpdateDTO,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    data_dict = update_data.model_dump(exclude_unset=True)

    # 普通用户不能修改自己的角色
    if "role" in data_dict:
        raise BusinessException(code=403, message="无权修改自己的角色")

    if "password" in data_dict:
        data_dict["password"] = hash_password(data_dict["password"])

    for key, value in data_dict.items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return Result.success(data=UserResponseDTO.model_validate(current_user))
