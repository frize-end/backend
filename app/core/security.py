from passlib.context import CryptContext

pwd_context = CryptContext(
    schemas=["bcrypt"],
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