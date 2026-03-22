from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base


class RefreshToken(Base):
    """Stores refresh tokens for JWT-based authentication."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, index=True)   # references PersonalInput.user_id

    token = Column(String(512), nullable=False, unique=True, index=True)
    is_revoked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<RefreshToken user_id={self.user_id} revoked={self.is_revoked}>"