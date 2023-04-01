"""empty message

Revision ID: 5680aa2d477e
Revises: 7d7aab2295ed
Create Date: 2023-03-31 19:56:39.477290

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5680aa2d477e'
down_revision = '7d7aab2295ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blog')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('content', mysql.TEXT(), nullable=False),
    sa.Column('author', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('date_added', mysql.DATETIME(), nullable=True),
    sa.Column('slug', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
