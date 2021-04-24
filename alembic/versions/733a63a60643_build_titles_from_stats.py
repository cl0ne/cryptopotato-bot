"""Build titles from stats

Revision ID: 733a63a60643
Revises: 981e95ceff06
Create Date: 2021-04-24 19:18:54.642211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "733a63a60643"
down_revision = "981e95ceff06"
branch_labels = None
depends_on = None


def upgrade():
    group_chats = sa.table(
        "daily_titles_group_chats",
        sa.column("chat_id", sa.BigInteger),
        sa.column("last_triggered", sa.DateTime),
        sa.column("last_titles", sa.Text),
        sa.column("last_given_titles_count", sa.Integer),
    )
    participants = sa.table(
        "daily_titles_participants",
        sa.column("id", sa.BigInteger),
        sa.column("chat_id", sa.BigInteger),
    )
    given_inevitable_titles = sa.table(
        "daily_titles_given_inevitable_titles",
        sa.column("id", sa.BigInteger),
        sa.column("given_on", sa.DateTime),
        sa.column("participant_id", sa.BigInteger),
    )
    given_shuffled_titles = sa.table(
        "daily_titles_given_shuffled_titles",
        sa.column("id", sa.BigInteger),
        sa.column("given_on", sa.DateTime),
        sa.column("participant_id", sa.BigInteger),
    )

    inevitable_count = (
        sa.select(sa.func.count(given_inevitable_titles.c.id))
        .join_from(
            given_inevitable_titles,
            participants,
            given_inevitable_titles.c.participant_id == participants.c.id,
        )
        .where(
            given_inevitable_titles.c.given_on == group_chats.c.last_triggered,
            participants.c.chat_id == group_chats.c.chat_id,
        )
    ).scalar_subquery()

    shuffled_count = (
        sa.select(sa.func.count(given_shuffled_titles.c.id))
        .join_from(
            given_shuffled_titles,
            participants,
            given_shuffled_titles.c.participant_id == participants.c.id,
        )
        .where(
            given_shuffled_titles.c.given_on == group_chats.c.last_triggered,
            participants.c.chat_id == group_chats.c.chat_id,
        )
    ).scalar_subquery()

    select_counts = sa.case(
        (group_chats.c.last_titles == None, None),
        else_=(inevitable_count + shuffled_count),
    )

    with op.batch_alter_table("daily_titles_group_chats", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("last_given_titles_count", sa.Integer(), nullable=True)
        )
    # we have to split the batch operation so last_given_titles_count will be present
    # when we are trying to calculate its values
    with op.batch_alter_table("daily_titles_group_chats", schema=None) as batch_op:
        batch_op.execute(
            group_chats.update().values(last_given_titles_count=select_counts)
        )
        batch_op.drop_column("last_titles_plain")
        batch_op.drop_column("last_titles")


def downgrade():
    with op.batch_alter_table("daily_titles_group_chats", schema=None) as batch_op:
        # Note that we don't generate contents for these columns from given_*_titles!
        batch_op.add_column(sa.Column("last_titles", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("last_titles_plain", sa.TEXT(), nullable=True))

        batch_op.drop_column("last_given_titles_count")
