from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, BigInteger, String, ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column


Base = declarative_base()


class ToiletCategory(Base):
    __tablename__ = 'toilet_category'
    toilet_id: Mapped[int] = mapped_column(ForeignKey('toilet.id'), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), primary_key=True)


class Category(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, unique=True)
    name: Mapped[str] = mapped_column(String(20), default='', unique=True, nullable=False)
    emoji: Mapped[str] = mapped_column(String(20), default='', unique=True)
    include_in_summary: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text('True'), nullable=False)
    graph_color: Mapped[str] = mapped_column(String(20), default='gray')
    toilets: Mapped[list['Toilet']] = relationship('Toilet', secondary='toilet_category', back_populates='categories')

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
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(BigInteger, default=0, unique=True, nullable=False)
    message_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    video_file_path: Mapped[str] = mapped_column(String(255), default='', nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)
    categories: Mapped[list['Category']] = relationship('Category', secondary='toilet_category', back_populates='toilets')

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'message_url': self.message_url,
            'video_file_path': self.video_file_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'categories': [c.to_dict() for c in self.categories],
        }
