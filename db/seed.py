# seed.py or scripts/seed_admin.py
from config import Config
from db.database import SessionLocal
from db.models.user import User
from utils.auth import get_password_hash


def seed_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == Config.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=Config.ADMIN_EMAIL,
                password=get_password_hash(Config.ADMIN_PASSWORD),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("✓ Admin user created")
        else:
            print("✓ Admin user already exists")
    finally:
        db.close()
