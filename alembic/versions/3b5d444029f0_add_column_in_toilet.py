"""add column in toilet

Revision ID: 3b5d444029f0
Revises: 5a55b0a1c9a1
Create Date: 2024-12-12 13:31:01.668050

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3b5d444029f0'
down_revision: Union[str, None] = '5a55b0a1c9a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE toilet ADD COLUMN url VARCHAR(255) AFTER video_file_path')
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('toilet', 'url')
    # ### end Alembic commands ###
