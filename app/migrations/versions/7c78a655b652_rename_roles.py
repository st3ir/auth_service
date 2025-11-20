"""rename roles

Revision ID: 7c78a655b652
Revises: b8c854782748
Create Date: 2024-12-28 03:06:01.002134

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7c78a655b652'
down_revision: Union[str, None] = 'c793bc20fa9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("""
        UPDATE role
        SET rolename = 'HR_SENIOR_EMPLOYEE'
        WHERE rolename = 'HR_CUSTOMER';
    """)
    op.execute("""
        UPDATE role
        SET rolename = 'HR_EMPLOYEE'
        WHERE rolename = 'USER_DEFAULT';
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE role
        SET rolename = 'HR_CUSTOMER'
        WHERE rolename = 'HR_SENIOR_EMPLOYEE';
    """)
    op.execute("""
        UPDATE role
        SET rolename = 'USER_DEFAULT'
        WHERE rolename = 'HR_EMPLOYEE';
    """)