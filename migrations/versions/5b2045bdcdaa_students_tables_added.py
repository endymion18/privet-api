"""Students tables added

Revision ID: 5b2045bdcdaa
Revises: 29ddc0ddce41
Create Date: 2024-01-13 17:02:33.486509

"""
from typing import Sequence, Union

import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b2045bdcdaa'
down_revision: Union[str, None] = '29ddc0ddce41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('students_relationship',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('buddy_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('arrival_id', sa.Integer(), nullable=False),
    sa.Column('student_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('student_photo', sa.String(length=1000), nullable=True),
    sa.Column('student_fullname', sa.String(length=320), nullable=True),
    sa.Column('student_citizenship', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['arrival_id'], ['arrival.id'], ),
    sa.ForeignKeyConstraint(['buddy_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['student_citizenship'], ['country.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('students_relationship')
    # ### end Alembic commands ###
