from logging import getLogger
from sqlalchemy.exc import SQLAlchemyError

from ..models import ToiletCategory
from ..session import get_db


logger = getLogger('bot')


def read_toilet_categories_by_tolet_id_all(toilet_id: int) -> list[ToiletCategory]:
    db = next(get_db())
    try:
        logger.info('Starting read read_toilet_category record by tolet_id.')
        records = db.query(ToiletCategory).filter(ToiletCategory.toilet_id == toilet_id).all()
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()

    return records


def create_toilet_category(toilet_id: int, category_id: int) -> None:
    db = next(get_db())
    try:
        logger.info('Starting create toilet_category record.')
        new = ToiletCategory(
            toilet_id=toilet_id,
            category_id=category_id,
        )

        db.add(new)
        db.commit()
        logger.info('Created new toilet_category record.')
    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()


def update_toilet_category(toilet_id: int, category_id: int) -> None:
    db = next(get_db())
    try:
        logger.info('Starting update toilet_category record.')
        record = db.query(ToiletCategory).filter(
            ToiletCategory.toilet_id == toilet_id,
        ).first()

        # DBに登録がなければ終了
        if record is None:
            logger.info('No record found to update.')
            return

        record.category_id = category_id
        db.commit()

    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()


def delete_toilet_category(toilet_id: int, category_id: int) -> None:
    db = next(get_db())
    try:
        logger.info('Starting delete toilet_category record.')
        records = db.query(ToiletCategory).filter(ToiletCategory.toilet_id == toilet_id).all()
        # DBに登録がなければ終了
        if records is None:
            logger.info('No record found to delete.')
            return

        # category_idが1のときは「ノーリアクション」なので、更新
        if len(records) == 1:
            records[0].category_id = 1
            db.commit()
        else:
            for r in records:
                if r.category_id == category_id:
                    db.delete(r)
                    db.commit()
                    logger.info('Deleted toilet_category record.')
                    break

    except SQLAlchemyError as e:
        logger.error(f'SQLAlchemyError: {e}')
        db.rollback()
    except Exception as e:
        logger.error(f'Unknown Error: {e}')
    finally:
        db.close()
