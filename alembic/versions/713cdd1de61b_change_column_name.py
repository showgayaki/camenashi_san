"""change column name

Revision ID: 713cdd1de61b
Revises: 3b5d444029f0
Create Date: 2024-12-12 16:47:47.668051

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '713cdd1de61b'
down_revision: Union[str, None] = '3b5d444029f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE toilet MODIFY category_id int(11) AFTER id')
    op.execute('ALTER TABLE toilet MODIFY url varchar(255) AFTER message_id')
    op.execute('ALTER TABLE toilet RENAME COLUMN url TO message_url')


def downgrade() -> None:
    op.execute('ALTER TABLE toilet MODIFY category_id int(11) AFTER message_id')
    op.execute('ALTER TABLE toilet MODIFY message_url varchar(255) AFTER video_file_path')
    op.execute('ALTER TABLE toilet RENAME COLUMN message_url TO url')
