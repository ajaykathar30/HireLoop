"""update_interview_session_statuses

Revision ID: 1eb1f3f83877
Revises: e28a369c17f3
Create Date: 2026-04-25 09:11:41.488118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1eb1f3f83877'
down_revision: Union[str, Sequence[str], None] = 'e28a369c17f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old constraint
    op.drop_constraint('interview_sessions_status_check', 'interview_sessions', type_='check')
    
    # Add new constraint with more statuses
    op.create_check_constraint(
        'interview_sessions_status_check',
        'interview_sessions',
        "status = ANY (ARRAY['pending'::text, 'ongoing'::text, 'in_progress'::text, 'completed'::text, 'expired'::text, 'cancelled'::text])"
    )


def downgrade() -> None:
    # Drop the new constraint
    op.drop_constraint('interview_sessions_status_check', 'interview_sessions', type_='check')
    
    # Revert to old statuses
    op.create_check_constraint(
        'interview_sessions_status_check',
        'interview_sessions',
        "status = ANY (ARRAY['pending'::text, 'in_progress'::text, 'completed'::text, 'cancelled'::text])"
    )
