"""alter tag model

Revision ID: 1683f50bbfc1
Revises: 533a799aee1a
Create Date: 2023-11-05 17:42:56.949462

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1683f50bbfc1"
down_revision = "533a799aee1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("tags", sa.Column("description", sa.String(), nullable=True))
    op.add_column("tags", sa.Column("company_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "tags", "companies", ["company_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "tags", type_="foreignkey")
    op.drop_column("tags", "company_id")
    op.drop_column("tags", "description")
    # ### end Alembic commands ###
