"""removed picture field from the Answer model

Revision ID: 7700e2b0d730
Revises: ea3fc145f654
Create Date: 2023-11-13 23:54:36.357197

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7700e2b0d730"
down_revision = "ea3fc145f654"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("answers", "picture_url")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "answers",
        sa.Column("picture_url", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
