from typing import List

from sqlalchemy import Column, Integer, String, Boolean, ARRAY, ForeignKey, DateTime, Float, func

from sqlalchemy.orm import relationship, Mapped, mapped_column

from models.BaseModel import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Enum


class User(BaseModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    city = Column(String(20), nullable=True)
    country = Column(String(20), nullable=True)
    phone = Column(String(13), nullable=True)
    status = Column(Boolean, nullable=True)
    roles = Column(ARRAY(String))
    companies = relationship("Company", back_populates="owner")
    invites = relationship("Action", back_populates="user", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    def to_dict(self):

        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'city': self.city,
            'country': self.country,
            'phone': self.phone,
            'status': self.status,
            'roles': self.roles,
        }

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class Company(BaseModel):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True, unique=False)
    description = Column(String, unique=False, nullable=True)
    site = Column(String, unique=False, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    is_visible = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    owner = relationship('User', back_populates='companies')
    quizzes: Mapped[List["Quiz"]] = relationship(cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="company")
    actions: Mapped[List["Action"]] = relationship(cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.username,
            'description': self.description,
            'city': self.city,
            'country': self.country,
            'is_visible': self.is_visible,
            'owner_id': self.owner_id
        }


class Action(BaseModel):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True)
    status = Column(Enum("PENDING", "REJECTED", "ACCEPTED", "CANCELLED", name="action_status"), nullable=False, default="pending")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="invites")
    type_of_action = Column(Enum("REQUEST", "INVITE", "MEMBER", name="type_of_action"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'type': self.type,

        }


class Quiz(BaseModel):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    question: Mapped[List["Question"]] = relationship(cascade="all, delete-orphan")
    quiz_result: Mapped[List["QuizResult"]] = relationship(cascade="all, delete-orphan")


class Question(BaseModel):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"))

    option: Mapped[List["Option"]] = relationship(cascade="all, delete-orphan")


class Option(BaseModel):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    is_correct = Column(Boolean, default=False)


class QuizResult(BaseModel):
    __tablename__ = "quiz_results"


    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey('users.id'))
    correct_answers = Column(Integer, nullable=False, default=0)
    questions = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, default=func.utcnow())
    company = relationship("Company", back_populates="quiz_results")
    user = relationship("User", back_populates="quiz_results")
    quiz_id:Mapped[int] = mapped_column(ForeignKey("quizzes.id"))


class Notification(BaseModel):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.timezone("UTC", func.now()), nullable=True)
    text = Column(String, nullable=False)
    status = Column(Enum("UNREAD", "READ", name="status_of_notification"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="notifications")
