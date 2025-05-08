from sqlalchemy import Column, Uuid, ForeignKey, DECIMAL, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.database import Base


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Uuid, primary_key=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(Uuid, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(DECIMAL(20, 8), nullable=False, default=0.0)
    locked_amount = Column(DECIMAL(20, 8), nullable=False, default=0.0)

    user = relationship("User", back_populates="balances")
    instrument = relationship("Instrument", back_populates="balances")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        CheckConstraint("locked_amount >= 0", name="check_locked_amount_positive"),
        UniqueConstraint('user_id', name='uq_user_balance')
    )