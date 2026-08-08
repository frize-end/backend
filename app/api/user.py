from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import (
    BusinessException,
    Result,
    create_access_token,
    get_current_user,
    get_db,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreateDTO, UserLoginDTO, UserResponseDTO, UserUpdateDTO

router = APIRouter(prefix="/user", tags=["用户管理"])

#新增用户
@router.post("", response_model=Result[UserResponseDTO])
def add_user(user_data: UserCreateDTO, db : Session = Depends(get_db),admin : User = Depends(get_current_user)):  # noqa: B008
    user = db.query(User).filter(User.username == user_data.username, User.is_delete == 0).first()
    hashed_pwd = hash_password(user_data.password)
    #检测用户是否存在
    if user:
        raise BusinessException(code=409, message="用户已存在")

    #创建新用户
    new_user = User(
        username=user_data.username,
        password=hashed_pwd,
        phone=user_data.phone,
        is_delete=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return Result.success(data=UserResponseDTO.model_validate(new_user))
#查询用户
@router.get("/{user_id}", response_model=Result[UserResponseDTO])
def get_user(user_id: int, db : Session = Depends(get_db),admin : User = Depends(get_current_user)):  # noqa: B008
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        raise BusinessException(code=404, message="用户不存在")
    return Result.success(data=UserResponseDTO.model_validate(user))

#更改用户信息
@router.patch("/{user_id}", response_model=Result[UserResponseDTO])
def update_user(user_id:int,update_data: UserUpdateDTO,db: Session = Depends(get_db),admin : User = Depends(get_current_user)):  # noqa: B008
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    #检测用户是否存在
    if not user :
        raise BusinessException(code=404, message="用户不存在")

    data_dict = update_data.model_dump(exclude_unset=True)

    if "password" in data_dict:
        data_dict["password"] = hash_password(data_dict["password"])

    for key,value in data_dict.items():
        setattr(user,key,value)
    db.commit()
    db.refresh(user)
    return Result.success(data=UserResponseDTO.model_validate(user))

#删除用户
@router.delete("/{user_id}", response_model=Result[None])
def delete_user(user_id:int,db: Session = Depends(get_db),admin : User = Depends(get_current_user)):  # noqa: B008
    #检测用户是否存在
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user :
        raise BusinessException(code=404, message="用户不存在")
    #逻辑删除
    user.is_delete = 1
    db.commit()
    return Result.success(message="删除成功")

#恢复删除的用户
@router.put("/{user_id}/restore", response_model=Result[UserResponseDTO])
def restore_user(user_id:int,db: Session = Depends(get_db),admin : User = Depends(get_current_user)):  # noqa: B008
    #检测用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user :
        raise BusinessException(code=404, message="用户不存在")
    #检测用户是否已删除
    if user.is_delete == 0:
        raise BusinessException(code=409, message="用户未被删除，无需恢复")
    #恢复用户
    user.is_delete = 0
    db.commit()
    return Result.success(data=UserResponseDTO.model_validate(user))

#用户登录
@router.post("/login", summary="用户登录", response_model=Result[dict])
def login(login_data: UserLoginDTO, db: Session = Depends(get_db)):  # noqa: B008
    user = db.query(User).filter(User.username == login_data.username, User.is_delete == 0).first()
    if not user or not verify_password(login_data.password, user.password):
        raise BusinessException(code=401,message="用户名或密码错误")

    access_token = create_access_token(data={"sub": str(user.id)})

    return Result.success(
        data={"access_token": access_token,
              "token_type": "bearer"})
    