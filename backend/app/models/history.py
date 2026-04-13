from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

try:
    from app.db.session import Base
except ImportError:
    from backend.app.db.session import Base

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Store the input and result of simulation
    input_data = Column(JSON)
    result_data = Column(JSON)
    
    owner = relationship("User", back_populates="histories")
