from datetime import datetime

from sqlalchemy import DECIMAL, TIMESTAMP, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow())
    password = Column(String(length=1024), nullable=False)
    auth0_registered = Column(Boolean, default=False, nullable=False)
    average_score = Column(DECIMAL, default=0)

    companies = relationship("CompanyUser", back_populates="users")

    def __repr__(self):
        return f"User {self.email}"
