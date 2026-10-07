"""create phone number for user column

Revision ID: cfcba9e82877
Revises: 
Create Date: 2026-10-06 07:31:17.615152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfcba9e82877'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone_number', sa.String(length=15), nullable=True)) #this will add a new column called phone_number to the users table. The column will be of type String with a maximum length of 15 characters and it will be nullable, meaning that it can contain null values. This is useful for storing phone numbers for users in the database.


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'phone_number') #this will drop the phone_number column from the users table. This is useful for rolling back the database schema to a previous state if needed.
