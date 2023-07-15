"""migration

Revision ID: 963a2596e216
Revises: 
Create Date: 2023-07-15 13:57:10.812311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '963a2596e216'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('city', sa.String(length=20), nullable=False),
    sa.Column('country', sa.String(length=20), nullable=False),
    sa.Column('phone', sa.String(length=13), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('roles', sa.ARRAY(sa.String()), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###