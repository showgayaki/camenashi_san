from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Toilet(Base):
    __tablename__ = 'toilet'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, default=0, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    video_file_path = Column(String(255), default='', nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), nullable=False)
    category = relationship('Category', back_populates='toilet')


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), default='', unique=True, nullable=False)
    emoji = Column(String(20), default='', unique=True, nullable=False)
