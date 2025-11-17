"""
Add user profile fields migration

This migration adds address and emergency contact fields to the users table
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_user_profile_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add new profile fields to users table"""
    # Address fields
    op.add_column('users', sa.Column('address_street', sa.String(), nullable=True))
    op.add_column('users', sa.Column('address_city', sa.String(), nullable=True))
    op.add_column('users', sa.Column('address_state', sa.String(), nullable=True))
    op.add_column('users', sa.Column('address_zip', sa.String(), nullable=True))
    op.add_column('users', sa.Column('address_country', sa.String(), nullable=True))
    
    # Emergency contact fields
    op.add_column('users', sa.Column('emergency_contact_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('emergency_contact_phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('emergency_contact_relationship', sa.String(), nullable=True))


def downgrade():
    """Remove profile fields from users table"""
    # Remove emergency contact fields
    op.drop_column('users', 'emergency_contact_relationship')
    op.drop_column('users', 'emergency_contact_phone')
    op.drop_column('users', 'emergency_contact_name')
    
    # Remove address fields
    op.drop_column('users', 'address_country')
    op.drop_column('users', 'address_zip')
    op.drop_column('users', 'address_state')
    op.drop_column('users', 'address_city')
    op.drop_column('users', 'address_street')
