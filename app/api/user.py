from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdateDTO

router = APIRouter(prefix="/user", tags=["用户管理"])

#新增用户
@router.post("")
def add_user(username: str, password: str, db : Session = Depends(get_db)):  # noqa: B008
    user = db.query(User).filter(User.username == username, User.is_delete == 0).first()
    #检测用户是否存在
    if user:
        raise ValueError("用户已存在")
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id":user.id,
        "username":user.username,
        "create_time":user.create_time
    }
#查询用户
@router.get("/user/{id}")
def get_user(id: int , db : Session = Depends(get_db)):  # noqa: B008
    user = db.query(User).filter(User.id == id, User.is_delete == 0).first()
    if not user:
        raise ValueError("用户不存在")
    return {
        "id":user.id,
        "username":user.username,
        "create_time":user.create_time
    }

#更改用户信息
@router.patch("/user/{user_id}")
def update_user(user_id:int,update_data: UserUpdateDTO,db: Session = Depends(get_db)):  # noqa: B008
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    #检测用户是否存在
    if not user :
        raise ValueError("用户不存在")

    data_dict = update_data.model_dump(exclude_unset=True)

    for key,value in data_dict.items():
        setattr(user,key,value)
    db.commit()
    db.refresh(user)
    return user

#删除用户
@router.delete("/user/{user_id}")
def delete_user(user_id:int,db: Session = Depends(get_db)):  # noqa: B008
    #检测用户是否存在
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user :
        raise ValueError("用户不存在")
    #逻辑删除
    user.is_delete = True
    db.commit()
    return {
    "message": "删除成功"
    }

#恢复删除的用户
@router.put("/user/{user_id}/restore")
def restore_user(user_id:int,db: Session = Depends(get_db)):  # noqa: B008
    #检测用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user :
        raise ValueError("用户不存在")
    #检测用户是否已删除
    if user.is_delete == 0:
        raise ValueError("用户已存在，无需恢复")
    #恢复用户
    user.is_delete = 0
    db.commit()
    return {
        "message": "恢复成功"
    }