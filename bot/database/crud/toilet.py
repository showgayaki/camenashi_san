from logging import getLogger
from datetime import datetime
from pathlib import Path
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from ..models import Category, Toilet
from ..session import get_db


logger = getLogger('bot')


def create_toilet(message_id: int, video_file_path: str, message_url: str, category_ids: list[int]) -> Toilet | None:
    db = next(get_db())
    # ファイル名から作成日時を取得
    try:
        created_at = datetime.strptime(
            Path(video_file_path).name.split('_')[0],
            '%Y%m%d-%H%M%S',
        )
    except Exception as e:
        # ファイル名から作成日時が取得できなかった場合はしょうがないので現在時刻を使用
        logger.error(f'Error occurred: {e}. Use current time instead.')
        created_at = datetime.now()

    new = Toilet(
        message_id=message_id,
        message_url=message_url,
        video_file_path=video_file_path,
        created_at=created_at,
        updated_at=created_at,
    )
    new.categories = db.query(Category).filter(Category.id.in_(category_ids)).all()

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


def read_toilet_by_message_id_with_categories(message_id: int) -> Toilet | None:
    db = next(get_db())
    record = None
    try:
        logger.info('Starting read toilet record with categories by message_id.')
        record = (
            db.query(Toilet)
            .options(joinedload(Toilet.categories))
            .filter(Toilet.message_id == message_id)
            .first()
        )
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()
    return record


def read_toilet_by_created_at_with_category(start: datetime, end: datetime) -> list[Toilet]:
    logger.info(f'Read DB: {start} ~ {end}')

    db = next(get_db())
    records = []

    try:
        logger.info('Starting read toilet records by created_at.')
        # Category.include_in_summary == Trueの「==」部分で、
        # comparison to True should be 'if cond is True:' or 'if cond:'Flake8(E712)
        # のエラーが出るが、WHERE句に相当する箇所なので「==」じゃないといけない(「is」じゃダメ)
        query = (
            select(Toilet)
            .join(Category, Toilet.categories)  # Updated to use the many-to-many relationship
            .options(joinedload(Toilet.categories))
            .where(
                and_(
                    Toilet.created_at >= start,
                    Toilet.created_at < end,
                    Category.include_in_summary == True,  # noqa: E712
                )
            )
            .order_by(Toilet.created_at)
        )

        records = db.execute(query).unique().scalars().all()
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()

    return list(records)


def update_toilet(message_id: int, category_ids: list[int]) -> tuple[int, int]:
    db = next(get_db())
    try:
        logger.info('Starting update toilet record.')
        record = db.query(Toilet).filter(Toilet.message_id == message_id).first()
        # DBに登録がなければ終了
        if record is None:
            logger.info('No record found to update.')
            return 0, 0

        logger.info(f'before: {record.to_dict()}')
        before = [c.id for c in record.categories][0]
        record.categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        db.commit()

        after = [c.id for c in record.categories][0]
        logger.info(f'after: {record.to_dict()}')
        logger.info(f'category_ids changed: {before} to {after}')
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
