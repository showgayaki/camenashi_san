"""add category

Revision ID: b0201cdc740a
Revises: 713cdd1de61b
Create Date: 2025-01-06 09:59:09.609084

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b0201cdc740a'
down_revision: Union[str, None] = '713cdd1de61b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('INSERT INTO category VALUES (3, "せず", "🥺", 1)')


def downgrade() -> None:
    # 「せず」のレコードはcategory_id=2にしておく
    op.execute('UPDATE toilet SET category_id = 2 WHERE category_id = 3')
    op.execute('DELETE FROM category WHERE id = 3')
