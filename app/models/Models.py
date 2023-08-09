

from sqlalchemy import Column, Integer, String, Boolean, ARRAY, ForeignKey

from sqlalchemy.orm import relationship

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



class Invitation(BaseModel):
    __tablename__ = "invitations"
    id = Column(Integer, primary_key=True)

    status = Column(Enum(PENDING="pending", REJECTED= "rejected", ACCEPTED="accepted"), nullable=False, default="pending")
    # ... other columns ...

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="invitations")

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="invitations")



class Request(BaseModel):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True)

    status = Column(Enum(PENDING="pending", REJECTED="rejected", ACCEPTED="accepted"), nullable=False,
                    default="pending")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="invitations")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="invitations")


