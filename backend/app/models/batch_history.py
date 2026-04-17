from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class BatchHistory(Base):
    __tablename__ = "batch_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    filename = Column(String, nullable=False, default="")
    is_ueg = Column(Boolean, default=False)
    apo_especial = Column(Boolean, default=False)
    total_linhas = Column(Integer, default=0)
    resultados = Column(JSON)

    owner = relationship("User", back_populates="batch_histories")
