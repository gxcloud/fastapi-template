"""Add OIDC and password salt columns to users

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_salt", sa.String(32), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("oidc_sub", sa.String(255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("oidc_provider", sa.String(50), nullable=True),
    )
    op.alter_column("users", "hashed_password", nullable=True)
    op.create_index(
        op.f("ix_users_oidc"), "users", ["oidc_provider", "oidc_sub"], unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_oidc"), table_name="users")
    op.alter_column("users", "hashed_password", nullable=False)
    op.drop_column("users", "oidc_provider")
    op.drop_column("users", "oidc_sub")
    op.drop_column("users", "password_salt")
