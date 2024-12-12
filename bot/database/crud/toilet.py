from logging import getLogger
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from ..models import Category, Toilet
from ..session import get_db


logger = getLogger('bot')


def create_toilet(message_id: int, video_file_path: str, message_url: str) -> Toilet | None:
    db = next(get_db())
    now = datetime.now()
    new = Toilet(
        category_id=1,
        message_id=message_id,
        video_file_path=video_file_path,
        message_url=message_url,
        created_at=now,
        updated_at=now,
    )

    try:
        logger.info('Starting create toilet record.')
        db.add(new)
        db.commit()
        logger.info(f'New Toilet record: {new.to_dict()}')
        return new
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()

    return None


def read_toilet_by_message_id(message_id: int) -> Toilet | None:
    db = next(get_db())
    record = None
    try:
        logger.info('Starting read toilet record by message_id.')
        record = db.query(Toilet).filter(Toilet.message_id == message_id).first()
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()

    return record


def read_toilet_by_created_at_with_category(start: datetime, end: datetime) -> list[Toilet]:
    logger.info(f'Start date: {start}')
    logger.info(f'End date: {end}')

    db = next(get_db())
    records = []

    try:
        logger.info('Starting read toilet records by created_at.')
        # Category.include_in_summary == Trueの「==」部分で、
        # comparison to True should be 'if cond is True:' or 'if cond:'Flake8(E712)
        # のエラーが出るが、WHERE句に相当する箇所なので「==」じゃないといけない(「is」じゃダメ)
        query = (
            select(Toilet)
            .join(Category, Toilet.category_id == Category.id)
            .options(joinedload(Toilet.category))
            .where(
                and_(
                    Toilet.created_at >= start,
                    Toilet.created_at < end,
                    Category.include_in_summary == True,  # noqa: E712
                )
            )
            .order_by(Toilet.created_at)
        )

        records = db.execute(query).scalars().all()
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()

    return records


def update_toilet(message_id: int, category_id: int) -> tuple[int, int]:
    db = next(get_db())
    try:
        logger.info('Starting update toilet record.')
        record = db.query(Toilet).filter(Toilet.message_id == message_id).first()
        # DBに登録がなければ終了
        if record is None:
            logger.info('No record found to update.')
            return

        logger.info(f'before: {record.to_dict()}')
        before = record.category_id
        record.category_id = category_id
        record.updated_at = datetime.now()
        db.commit()

        after = record.category_id
        logger.info(f'after: {record.to_dict()}')
        logger.info(f'category_id changed: {before} to {after}')
        logger.info('Toilet record updated successfully.')
        return before, after
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()

    return 0, 0
