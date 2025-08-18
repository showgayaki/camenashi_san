from logging import getLogger
import subprocess
import shlex

from utils.config import ConfigManager

logger = getLogger('bot')
config = ConfigManager().config


def backup_db() -> str:
    """
    BACKUP_COMMAND に設定された外部スクリプトを実行して
    バックアップ処理を行う。
    """
    if not config.BACKUP_COMMAND:
        logger.error('BACKUP_COMMAND is not set in config.')
        return 'BACKUP_COMMAND は設定されてないでやんす'

    try:
        logger.info(f'Starting backup: {config.BACKUP_COMMAND}')
        # shlex.split で ["path", "--db", "camenashi"] のように分解
        result = subprocess.run(
            shlex.split(config.BACKUP_COMMAND),
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f'Backup completed successfully. stdout: {result.stdout.strip()}')
        if result.stderr:
            logger.warning(f'Backup stderr: {result.stderr.strip()}')

        reply = 'DBのバックアップに成功したでやんす'
    except subprocess.CalledProcessError as e:
        logger.error(f'Backup failed with return code {e.returncode}. stderr: {e.stderr.strip()}')
        reply = _handle_backup_error(e)
    except Exception as e:
        logger.exception(f'Unexpected error during backup: {e}')
        reply = _handle_backup_error(e)

    return reply


def _handle_backup_error(e: Exception) -> str:
    return f'DBのバックアップに失敗したでやんす:\n{e}'
