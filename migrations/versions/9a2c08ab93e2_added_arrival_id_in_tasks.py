"""added arrival id in tasks

Revision ID: 9a2c08ab93e2
Revises: 179d6a1f1176
Create Date: 2024-01-11 12:33:35.421376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a2c08ab93e2'
down_revision: Union[str, None] = '179d6a1f1176'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profile_tasks', sa.Column('arrival_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'profile_tasks', 'arrival', ['arrival_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'profile_tasks', type_='foreignkey')
    op.drop_column('profile_tasks', 'arrival_id')
    # ### end Alembic commands ###
