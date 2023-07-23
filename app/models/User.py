from sqlalchemy import Column, Integer, String, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    city = Column(String(20), nullable=False)
    country = Column(String(20), nullable=False)
    phone = Column(String(13), nullable=False)
    status = Column(Boolean, nullable=False)
    roles = Column(ARRAY(String))

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



