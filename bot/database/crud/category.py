from logging import getLogger
from sqlalchemy.exc import SQLAlchemyError

from ..models import Category
from ..session import get_db


logger = getLogger('bot')


def read_category(id: int = 0, emoji: str = '') -> Category:
    db = next(get_db())
    category = None
    try:
        logger.info('Starting read category record.')
        category = (db.query(Category).filter(Category.id == id).first()
                    if id else db.query(Category).filter(Category.emoji == emoji).first())
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()

    return category
