from sqlalchemy import Column, Uuid, ForeignKey, DECIMAL, DateTime, func, Enum, Index

from src.core.database import Base
from src.order.enums import Direction, OrderStatus, OrderType


class Order(Base):
    __tablename__ = "orders"

    id = Column(Uuid, primary_key=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(Uuid, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    direction = Column(Enum(Direction), nullable=False)
    price = Column(DECIMAL(20, 8))
    quantity = Column(DECIMAL(20, 8), nullable=False)
    filled_quantity = Column(DECIMAL(20, 8), nullable=False, default=0.0)
    status = Column(Enum(OrderStatus), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        Index('ix_orders_user_id', 'user_id'),
    )