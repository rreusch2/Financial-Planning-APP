"""Ensure all models are up-to-date

Revision ID: a736dbf967f8
Revises: 1c637f52ee52
Create Date: 2024-11-12 00:46:21.635559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a736dbf967f8'
down_revision = '1c637f52ee52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=128),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=128),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.alter_column('username',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)

    # ### end Alembic commands ###
