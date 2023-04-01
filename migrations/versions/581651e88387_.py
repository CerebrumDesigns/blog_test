"""empty message

Revision ID: 581651e88387
Revises: 984e31a63ad2
Create Date: 2023-03-31 12:54:18.134306

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '581651e88387'
down_revision = '984e31a63ad2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('add_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('add_user', schema=None) as batch_op:
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###
