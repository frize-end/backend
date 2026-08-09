from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

def create_admin():
    db = SessionLocal()
    try:
        # 检查管理员是否已存在
        admin = db.query(User).filter(User.username == "admin", User.is_delete == 0).first()
        if admin:
            print("管理员已存在")
            return

        admin = User(username="admin",
                      password=hash_password("admin123"),
                      phone="13210533587",
                      role="admin",
                      is_delete=0
                      )
        db.add(admin)