from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from utils.config import ConfigManager

# 設定の読み込み
config = ConfigManager().config

# データベースエンジンの作成
engine = create_engine(
    'mariadb+mariadbconnector://{}:{}@{}:{}/{}'.format(
        config.DB_USER, config.DB_PASS, config.DB_HOST, config.DB_PORT, config.DB_NAME
    ),
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

# セッションの作成
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
