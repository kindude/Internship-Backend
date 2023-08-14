"""empty message

Revision ID: b3c294c31f33
Revises: 2068f6be11eb
Create Date: 2023-08-13 01:50:37.225940

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b3c294c31f33'
down_revision = '2068f6be11eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('actions', sa.Column('type_of_action', sa.Enum('REQUEST', 'INVITE', 'MEMBER', name='type_of_action'), nullable=False))
    op.drop_column('actions', 'type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('actions', sa.Column('type', postgresql.ENUM('REQUEST', 'INVITE', name='type_of_action'), autoincrement=False, nullable=False))
    op.drop_column('actions', 'type_of_action')
    # ### end Alembic commands ###
