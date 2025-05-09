from sqlalchemy import Column, Uuid, ForeignKey, DECIMAL, UniqueConstraint, Index

from src.core.database import Base


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Uuid, primary_key=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(Uuid, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(DECIMAL(20, 8), nullable=False, default=0.0)
    locked_amount = Column(DECIMAL(20, 8), nullable=False, default=0.0)

    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_balance'),
        Index('ix_balances_user_id', 'user_id')
    )