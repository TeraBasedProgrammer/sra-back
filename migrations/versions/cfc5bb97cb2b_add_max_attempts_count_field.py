"""add max_attempts_count field

Revision ID: cfc5bb97cb2b
Revises: e8c0d95eb517
Create Date: 2023-11-27 20:52:33.659737

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cfc5bb97cb2b"
down_revision = "e8c0d95eb517"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "quizzes",
        sa.Column("max_attempts_count", sa.Integer(), nullable=False, default=1),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("quizzes", "max_attempts_count")
    # ### end Alembic commands ###
