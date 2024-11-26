from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from .models import Toilet, Category
from .session import get_db


def create_toilet(
    message_id: int,
    video_file_path: str,
    created_at: datetime = datetime.now(),
    updated_at: datetime = datetime.now()
) -> None:
    db = next(get_db())
    new = Toilet(
        category_id=1,
        message_id=message_id,
        video_file_path=video_file_path,
        created_at=created_at,
        updated_at=updated_at,
    )
    try:
        db.add(new)
        db.commit()
        db.refresh(new)
    except SQLAlchemyError as e:
        print(e)
        db.rollback()
    finally:
        db.close()


def update_toilet(message_id: int, category_id: int) -> None:
    db = next(get_db())
    try:
        record = db.query(Toilet).filter(Toilet.message_id == message_id).first()
        record.category_id = category_id
        db.commit()
        db.refresh(record)
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()


def read_category(emoji: str) -> int:
    db = next(get_db())
    category_id = 0
    try:
        record = db.query(Category).filter(Category.emoji == emoji).first()
        category_id = record.id
    except SQLAlchemyError as e:
        print(e)
    finally:
        db.close()

    return category_id
