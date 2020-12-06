"""Update naming conventions

Revision ID: f786ea9057b0
Revises: 42ff42f8516a
Create Date: 2020-12-06 04:04:07.891327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f786ea9057b0"
down_revision = "42ff42f8516a"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("daily_titles_participants", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_daily_titles_participants_user_id_chat_id"),
            ["user_id", "chat_id"],
        )
        batch_op.drop_constraint("uq_daily_titles_participants_user_id", type_="unique")


def downgrade():
    with op.batch_alter_table("daily_titles_participants", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_daily_titles_participants_user_id", ["user_id", "chat_id"]
        )
        batch_op.drop_constraint(
            batch_op.f("uq_daily_titles_participants_user_id_chat_id"), type_="unique"
        )
