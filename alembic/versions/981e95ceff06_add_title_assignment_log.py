"""Add title assignment log

Revision ID: 981e95ceff06
Revises: f786ea9057b0
Create Date: 2020-12-06 20:50:53.222690

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "981e95ceff06"
down_revision = "f786ea9057b0"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("daily_titles_assignment_records")
    op.create_table(
        "daily_titles_given_inevitable_titles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("title_id", sa.Integer(), nullable=False),
        sa.Column(
            "given_on",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column("streak_length", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["daily_titles_participants.id"],
            name=op.f(
                "fk_daily_titles_given_inevitable_titles_participant_id_daily_titles_participants"
            ),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["title_id"],
            ["daily_titles_inevitable_titles.id"],
            name=op.f(
                "fk_daily_titles_given_inevitable_titles_title_id_daily_titles_inevitable_titles"
            ),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_daily_titles_given_inevitable_titles")
        ),
    )

    op.create_table(
        "daily_titles_given_shuffled_titles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("title_id", sa.Integer(), nullable=False),
        sa.Column(
            "given_on",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["daily_titles_participants.id"],
            name=op.f(
                "fk_daily_titles_given_shuffled_titles_title_id_daily_titles_shuffled_titles"
            ),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["title_id"],
            ["daily_titles_shuffled_titles.id"],
            name=op.f(
                "fk_daily_titles_given_shuffled_titles_title_id_daily_titles_shuffled_titles"
            ),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_daily_titles_given_shuffled_titles")
        ),
    )


def downgrade():
    op.drop_table("daily_titles_given_inevitable_titles")
    op.create_table(
        "daily_titles_assignment_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("title_id", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("last_assigned_on", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["daily_titles_participants.id"],
            name=op.f(
                "fk_daily_titles_assignment_records_participant_id_daily_titles_participants"
            ),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["title_id"],
            ["daily_titles_inevitable_titles.id"],
            name=op.f(
                "fk_daily_titles_assignment_records_title_id_daily_titles_inevitable_titles"
            ),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_titles_assignment_records")),
        sa.UniqueConstraint(
            "participant_id",
            "title_id",
            name=op.f("uq_daily_titles_assignment_records_participant_id"),
        ),
    )

    op.drop_table("daily_titles_given_shuffled_titles")
