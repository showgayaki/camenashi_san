from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from utils.config import load_config

# 設定の読み込み
config = load_config()

# データベースエンジンの作成
engine = create_engine(
    'mariadb+mariadbconnector://{}:{}@{}:{}/{}'.format(
        config.DB_HOST, config.DB_PASS, config.DB_HOST, config.DB_PORT, config.DB_NAME
    ),
    echo=True
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
