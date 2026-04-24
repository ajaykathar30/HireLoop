"""fix embeddings type

Revision ID: d4e1dfd55cc5
Revises: c56dacc53f33
Create Date: 2026-04-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = 'd4e1dfd55cc5'
down_revision = 'c56dacc53f33'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Create extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # 2. Fix candidates table
    op.alter_column('candidates', 'resume_embedding',
               type_=Vector(768),
               postgresql_using='resume_embedding::vector')

    # 3. Fix jobs table
    op.alter_column('jobs', 'job_embedding',
               type_=Vector(768),
               postgresql_using='job_embedding::vector')

def downgrade():
    op.alter_column('jobs', 'job_embedding',
               existing_type=Vector(768),
               type_=sa.NullType())
    op.alter_column('candidates', 'resume_embedding',
               existing_type=Vector(768),
               type_=sa.NullType())
