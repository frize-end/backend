from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import get_db
from app.core.exceptions import BusinessException
from app.models.user import User

settings = Settings()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(plain_password: str) -> str:
    """
    明文密码加密成密文
    :param plain_password: 用户输入的明文密码
    :return: 加密后的密文，存数据库
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码和密文是否匹配
    :param plain_password: 用户登录输入的明文密码
    :param hashed_password: 数据库里存的密文密码
    :return: 匹配返回True，不匹配返回False
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict) -> str:
    """
    生成JWT访问令牌
    :param data: 要存到令牌里的用户信息，一般存用户ID，比如{"sub": "1"}
    :return: JWT字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})  # exp是JWT标准的过期时间字段
    
    # 生成令牌：用密钥和算法签名
    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    校验JWT令牌是否合法
    :param token: 前端传过来的JWT字符串
    :return: 令牌里存的用户信息
    :raises: 令牌无效/过期抛401业务异常
    """
    try:
        # 解析并验证令牌，签名不对、过期都会抛JWTError
        payload = jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        # 任何验证失败（过期、篡改、伪造）都抛401异常，和全局异常对接
        raise BusinessException(code=401, message="无效的登录凭证，请重新登录")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)  # noqa: B008
)  -> User:
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise BusinessException(code=401, message="无效的登录凭证，请重新登录")
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        raise  BusinessException(code=401, message="用户不存在或已被删除")
    return user