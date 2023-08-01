
from sqlalchemy import Column, Integer, String, Boolean, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(50), unique=True, nullable=False)
    city = Column(String(20), nullable=False)
    country = Column(String(20), nullable=False)
    is_visible = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', back_populates='companies')

