"""Drop GroupChat.copy_default_titles

Revision ID: 42ff42f8516a
Revises: 564bfe5ee644
Create Date: 2020-10-06 21:11:13.551185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "42ff42f8516a"
down_revision = "564bfe5ee644"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("daily_titles_group_chats", schema=None) as batch_op:
        batch_op.drop_column("copy_default_titles")


def downgrade():
    with op.batch_alter_table("daily_titles_group_chats", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("copy_default_titles", sa.BOOLEAN(), nullable=False)
        )
