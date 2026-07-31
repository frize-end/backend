from app.core.database import Base, engine
from app.models.user import User  # noqa: F401


def create_tables():
    Base.metadata.create_all(bind = engine)
    print("所有数据库表创建成功")

if __name__ == "__main__":
    create_tables()