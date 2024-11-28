from datetime import datetime
from logging import getLogger
from sqlalchemy.exc import SQLAlchemyError

from .models import Toilet, Category
from .session import get_db


logger = getLogger(__name__)


def create_toilet(message_id: int, video_file_path: str) -> Toilet:
    db = next(get_db())
    now = datetime.now()
    new = Toilet(
        category_id=1,
        message_id=message_id,
        video_file_path=video_file_path,
        created_at=now,
        updated_at=now,
    )

    try:
        logger.info('Starting create toilet record.')
        db.add(new)
        db.commit()
        return new
    except SQLAlchemyError as e:
        logger.error(e)
        db.rollback()
    finally:
        db.close()


def update_toilet(message_id: int, category_id: int) -> None:
    db = next(get_db())
    try:
        logger.info('Starting update toilet record.')
        record = db.query(Toilet).filter(Toilet.message_id == message_id).first()
        record.category_id = category_id
        db.commit()
        db.refresh(record)
    except SQLAlchemyError as e:
        logger.error(e)
        db.rollback()
    finally:
        db.close()


def read_category(id: int = 0, emoji: str = '') -> Category:
    db = next(get_db())
    category = None
    try:
        logger.info('Starting read category record.')
        category = (db.query(Category).filter(Category.id == id).first()
                    if id else db.query(Category).filter(Category.emoji == emoji).first())
        logger.info(f'category_id: {category.id}.')
        return category
    except SQLAlchemyError as e:
        logger.error(e)
    finally:
        db.close()

    return category
