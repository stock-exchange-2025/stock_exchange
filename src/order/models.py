from sqlalchemy import Column, Uuid, ForeignKey, DECIMAL, CheckConstraint, DateTime, func, Enum
from sqlalchemy.orm import relationship

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

    user = relationship("User", back_populates="orders")
    instrument = relationship("Instrument", back_populates="orders")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("filled_quantity >= 0 AND filled_quantity <= quantity", name="check_filled_quantity"),
        CheckConstraint("(price > 0 AND order_type = 'limit') OR (order_type = 'market')", name="check_price"),
    )