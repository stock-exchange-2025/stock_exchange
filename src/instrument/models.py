from sqlalchemy import Column, Uuid, String
from sqlalchemy.orm import relationship

from src.core.database import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Uuid, primary_key=True)
    ticker = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)

    balances = relationship("Balance", back_populates="instrument")
    orders = relationship("Order", back_populates="instrument")
    transactions = relationship("Transaction", back_populates="instrument")