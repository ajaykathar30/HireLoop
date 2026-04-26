"""add_shortlisted_to_application_status

Revision ID: e5060454a294
Revises: d4e1dfd55cc5
Create Date: 2026-04-25 07:13:27.671962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5060454a294'
down_revision: Union[str, Sequence[str], None] = 'd4e1dfd55cc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old constraint
    op.drop_constraint('applications_status_check', 'applications', type_='check')
    
    # Add the new constraint with 'shortlisted' included
    op.create_check_constraint(
        'applications_status_check',
        'applications',
        "status = ANY (ARRAY['applied'::text, 'screening'::text, 'shortlisted'::text, 'interview_scheduled'::text, 'interviewed'::text, 'recommended'::text, 'rejected'::text])"
    )


def downgrade() -> None:
    # Drop the new constraint
    op.drop_constraint('applications_status_check', 'applications', type_='check')
    
    # Revert to the old constraint (without 'shortlisted')
    op.create_check_constraint(
        'applications_status_check',
        'applications',
        "status = ANY (ARRAY['applied'::text, 'screening'::text, 'interview_scheduled'::text, 'interviewed'::text, 'recommended'::text, 'rejected'::text])"
    )
