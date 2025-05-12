from sqlalchemy import Uuid, func, Column, DECIMAL, DateTime, ForeignKey

from src.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Uuid, primary_key=True)
    order_id = Column(Uuid, ForeignKey("orders.id", ondelete="SET NULL"))
    instrument_id = Column(Uuid, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False)
    price = Column(DECIMAL(20, 8), nullable=False)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    executed_at = Column(DateTime, server_default=func.current_timestamp())