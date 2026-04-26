"""add_new_notification_types

Revision ID: 8769bb49450c
Revises: e5060454a294
Create Date: 2026-04-25 07:53:30.041648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8769bb49450c'
down_revision: Union[str, Sequence[str], None] = 'e5060454a294'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old constraint
    op.drop_constraint('notifications_type_check', 'notifications', type_='check')
    
    # Add new constraint with more types
    op.create_check_constraint(
        'notifications_type_check',
        'notifications',
        "type = ANY (ARRAY['application_update'::text, 'interview_scheduled'::text, 'report_ready'::text, 'shortlisted'::text, 'rejected'::text])"
    )


def downgrade() -> None:
    # Drop the new constraint
    op.drop_constraint('notifications_type_check', 'notifications', type_='check')
    
    # Revert to old types
    op.create_check_constraint(
        'notifications_type_check',
        'notifications',
        "type = ANY (ARRAY['application_update'::text, 'interview_scheduled'::text, 'report_ready'::text])"
    )
