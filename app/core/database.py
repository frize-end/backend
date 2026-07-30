from sqlalchemy import create_engine
from sqlalchemy.orm import Declarative_base, sessionmaker

DB_URL = "mysql+pymysql://root:123456@localhost:3306/fastapi_demo?charset=utf8mb4"

# 创建数据库连接引擎
engine = create_engine(
    DB_URL,
    pool_size=10,
    max_overflow=20,
    echo=True
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)
# 创建数据库映射基类
class Base(Declarative_base):
     pass
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
