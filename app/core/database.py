from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import Settings

settings = Settings()

DB_URL = f"mysql+pymysql://{settings.user}@{settings.user_password}:{settings.db_port}/{settings.db_name}?charset=utf8mb4"

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
class Base(DeclarativeBase):
     pass
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
