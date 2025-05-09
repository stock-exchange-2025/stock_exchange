from sqlalchemy import Column, Uuid, String, Index

from src.core.database import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Uuid, primary_key=True)
    ticker = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)

    __table_args__ = (
        Index('ix_instruments_ticker', 'ticker'),
    )