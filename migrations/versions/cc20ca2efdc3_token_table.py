"""token_table

Revision ID: cc20ca2efdc3
Revises: e0dfe00f8e1c
Create Date: 2023-11-02 14:29:17.613831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc20ca2efdc3'
down_revision: Union[str, None] = 'e0dfe00f8e1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('token', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['email'], ['user.email'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('token')
    # ### end Alembic commands ###