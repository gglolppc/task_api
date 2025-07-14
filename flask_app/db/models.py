from flask_app.db.database import Base
from sqlalchemy import String, Integer, ForeignKey, Column, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String, nullable=False, server_default='Unknown')
    password = Column(String)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    tasks = relationship('Task', back_populates='users', cascade='all, delete-orphan')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    deadline = Column(DateTime)
    priority = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    users = relationship('User', back_populates='tasks')
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'deadline': self.deadline,
            'priority': self.priority,
        }
