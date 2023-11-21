import enum
from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


# RoleEnum("owner")
class RoleEnum(enum.Enum):
    Owner = "owner"
    Admin = "admin"
    Tester = "tester"
    Employee = "employee"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())

    users = relationship("CompanyUser", back_populates="companies", lazy="select")

    def __repr__(self) -> str:
        return f"Company '{self.title}'"


class CompanyUser(Base):
    __tablename__ = "company_user"

    company_id = Column(
        ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.Owner)

    users = relationship("User", back_populates="companies", lazy="joined")
    companies = relationship("Company", back_populates="users", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"CompanyUser object for company {self.company_id} and user {self.user_id}"
        )
