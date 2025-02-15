from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship


Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=False, unique=True)
    name = Column(String(20), default='', unique=True, nullable=False)
    emoji = Column(String(20), default='', unique=True)
    include_in_summary = Column(Boolean, default=True, server_default=text('True'), nullable=False)
    graph_color = Column(String(20), default='gray')
    toilet = relationship('Toilet', back_populates='category')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'include_in_summary': self.include_in_summary,
            'graph_color': self.graph_color,
        }


class Toilet(Base):
    __tablename__ = 'toilet'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    message_id = Column(BigInteger, default=0, unique=True, nullable=False)
    message_url = Column(String(255), nullable=True)
    video_file_path = Column(String(255), default='', nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), nullable=False)
    category = relationship('Category', back_populates='toilet')

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'message_id': self.message_id,
            'message_url': self.message_url,
            'video_file_path': self.video_file_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
