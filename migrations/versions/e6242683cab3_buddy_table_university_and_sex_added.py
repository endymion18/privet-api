"""buddy table university and sex added

Revision ID: e6242683cab3
Revises: 7cb1ec83df46
Create Date: 2023-11-09 19:51:11.914091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6242683cab3'
down_revision: Union[str, None] = '7cb1ec83df46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profile_buddy', sa.Column('university', sa.Integer(), nullable=True))
    op.add_column('profile_buddy', sa.Column('sex', sa.String(length=6), nullable=True))
    op.create_foreign_key(None, 'profile_buddy', 'university', ['university'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'profile_buddy', type_='foreignkey')
    op.drop_column('profile_buddy', 'sex')
    op.drop_column('profile_buddy', 'university')
    # ### end Alembic commands ###
