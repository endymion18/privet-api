"""chats and messages2

Revision ID: 26aa5dc95d78
Revises: a6c10ea79bb3
Create Date: 2023-12-25 18:24:46.406593

"""
from typing import Sequence, Union
import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26aa5dc95d78'
down_revision: Union[str, None] = 'a6c10ea79bb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('first_user', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('second_user', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['first_user'], ['user.id'], ),
    sa.ForeignKeyConstraint(['second_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('from_user', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('date_print', sa.DateTime(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('attachment', sa.String(), nullable=False),
    sa.Column('read', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.ForeignKeyConstraint(['from_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    op.drop_table('chat')
    # ### end Alembic commands ###
