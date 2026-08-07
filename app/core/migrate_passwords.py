# migrate_passwords.py
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def migrate():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_delete == 0).all()
        for user in users:
            # 判断是否是明文（bcrypt哈希都是$2b$开头）
            if not user.password.startswith("$2b$"):
                user.password = hash_password(user.password)
                print(f"已迁移用户: {user.username}")
        db.commit()
        print("迁移完成")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()