"""Daily titles models

Revision ID: 564bfe5ee644
Revises: 
Create Date: 2020-05-02 22:17:14.616669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '564bfe5ee644'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'daily_titles_group_chats',

        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('is_migration_conflicted', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('copy_default_titles', sa.Boolean(), nullable=False),
        sa.Column('last_triggered', sa.DateTime(), nullable=True),
        sa.Column('last_titles', sa.Text(), nullable=True),
        sa.Column('last_titles_plain', sa.Text(), nullable=True),

        sa.PrimaryKeyConstraint('chat_id', name=op.f('pk_daily_titles_group_chats'))
    )
    op.create_table(
        'daily_titles_title_templates',

        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=255), nullable=False),
        sa.Column('is_inevitable', sa.Boolean(), nullable=False),

        sa.PrimaryKeyConstraint('id', name=op.f('pk_daily_titles_title_templates'))
    )
    op.create_table(
        'daily_titles_inevitable_titles',

        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('text', sa.String(length=255), nullable=False),

        sa.ForeignKeyConstraint(
            ['chat_id'], ['daily_titles_group_chats.chat_id'],
            name=op.f('fk_daily_titles_inevitable_titles_chat_id_daily_titles_group_chats'),
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_daily_titles_inevitable_titles'))
    )
    op.create_table(
        'daily_titles_participants',

        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=32), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_missing', sa.Boolean(), server_default=sa.false(), nullable=False),

        sa.ForeignKeyConstraint(
            ['chat_id'], ['daily_titles_group_chats.chat_id'],
            name=op.f('fk_daily_titles_participants_chat_id_daily_titles_group_chats'),
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_daily_titles_participants')),
        sa.UniqueConstraint('user_id', 'chat_id', name=op.f('uq_daily_titles_participants_user_id'))
    )

    op.create_table(
        'daily_titles_shuffled_titles',

        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('text', sa.String(length=255), nullable=False),
        sa.Column('roll_order', sa.Integer(), nullable=True),

        sa.ForeignKeyConstraint(
            ['chat_id'], ['daily_titles_group_chats.chat_id'],
            name=op.f('fk_daily_titles_shuffled_titles_chat_id_daily_titles_group_chats'),
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_daily_titles_shuffled_titles'))
    )
    with op.batch_alter_table('daily_titles_shuffled_titles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_daily_titles_shuffled_titles_roll_order'), ['roll_order'], unique=False)

    op.create_table(
        'daily_titles_assignment_records',

        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('title_id', sa.Integer(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('last_assigned_on', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(
            ['participant_id'], ['daily_titles_participants.id'],
            name=op.f('fk_daily_titles_assignment_records_participant_id_daily_titles_participants'),
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['title_id'], ['daily_titles_inevitable_titles.id'],
            name=op.f('fk_daily_titles_assignment_records_title_id_daily_titles_inevitable_titles'),
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_daily_titles_assignment_records')),
        sa.UniqueConstraint('participant_id', 'title_id',
                            name=op.f('uq_daily_titles_assignment_records_participant_id'))
    )


def downgrade():
    op.drop_table('daily_titles_assignment_records')
    with op.batch_alter_table('daily_titles_shuffled_titles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_daily_titles_shuffled_titles_roll_order'))

    op.drop_table('daily_titles_shuffled_titles')
    op.drop_table('daily_titles_participants')
    op.drop_table('daily_titles_inevitable_titles')
    op.drop_table('daily_titles_title_templates')
    op.drop_table('daily_titles_group_chats')
