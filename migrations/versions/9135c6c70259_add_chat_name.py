"""Add chat name

Revision ID: 9135c6c70259
Revises: b93c61e70097
Create Date: 2024-09-17 17:37:57.971346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9135c6c70259'
down_revision: Union[str, None] = 'b93c61e70097'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('name', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'name')
    # ### end Alembic commands ###
