"""Update category name

Revision ID: 47a7ccc37e55
Revises: 910dc124641b
Create Date: 2024-12-03 00:09:10.848733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47a7ccc37e55'
down_revision: Union[str, None] = '910dc124641b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # categoryテーブルを更新
    op.execute(
        sa.text(
            "UPDATE category SET name = 'しーしー' WHERE name = 'おしーしー'"
        )
    )


def downgrade() -> None:
    # 変更を元に戻すコード
    op.execute(
        sa.text(
            "UPDATE category SET name = 'おしーしー' WHERE name = 'しーしー'"
        )
    )
