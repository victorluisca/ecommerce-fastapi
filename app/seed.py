from sqlmodel import Session, select

from app.config import settings
from app.core.security import hash_password
from app.database import engine
from app.models.user import User, UserRole


def create_admin():
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.email == "admin@example.com")
        ).first()

        if existing:
            print("Admin user already exists")
            return

        admin = User(
            full_name=settings.admin_full_name,
            email=settings.admin_email,
            hashed_password=hash_password(settings.admin_password),
            role=UserRole.ADMIN,
        )

        session.add(admin)
        session.commit()

        print("Admin user created: admin@example.com / AdminPassword123!")


if __name__ == "__main__":
    create_admin()
