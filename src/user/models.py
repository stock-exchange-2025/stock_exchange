from sqlalchemy import Column, String, Uuid, func, DateTime, Enum, UniqueConstraint

from src.core.database import Base
from src.user.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    role = Column(Enum(UserRole), nullable=False)
    api_key = Column(String(512), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        UniqueConstraint('username', name='uq_users_username'),
        UniqueConstraint('api_key', name='uq_users_api_key')
    )