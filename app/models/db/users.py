from datetime import datetime

from sqlalchemy import (DECIMAL, TIMESTAMP, Boolean, Column, ForeignKey,
                        Integer, String)
from sqlalchemy.orm import relationship

from .attempts import Attempt
from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow())
    password = Column(String(length=1024), nullable=False)
    auth0_registered = Column(Boolean, default=False, nullable=False)
    average_score = Column(DECIMAL, default=0)

    companies = relationship("CompanyUser", back_populates="users", lazy='joined')
    tags = relationship("TagUser", back_populates="users", lazy='joined')
    attempts = relationship("Attempt", back_populates="user", lazy='joined') 

    def __repr__(self):
        return f"User {self.email}"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True)
    
    users = relationship("TagUser", back_populates="tags")
    quizzes = relationship("TagQuiz", back_populates="tags")


class TagUser(Base):
    __tablename__ = "tag_user"

    tag_id = Column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    users = relationship("User", back_populates="tags", lazy='subquery') 
    tags = relationship("Tag",  back_populates="users", lazy='subquery')


class TagQuiz(Base):
    __tablename__ = "tag_quiz"

    tag_id = Column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    quiz_id = Column(ForeignKey("quizzes.id", ondelete="CASCADE"), primary_key=True)

    quizzes = relationship("Quiz", back_populates="tags", lazy='subquery') 
    tags = relationship("Tag",  back_populates="quizzes", lazy='subquery')