"""Initial Commit

Revision ID: 188d0c4a3762
Revises: 
Create Date: 2025-03-17 12:02:28.955385

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '188d0c4a3762'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('role', postgresql.ENUM('user', 'doctor', 'moderator', 'pharmacist', 'admin', name='user_role'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('chat',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_detail',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('age', sa.String(length=3), nullable=False),
    sa.Column('height', sa.String(length=10), nullable=False),
    sa.Column('weight', sa.String(length=10), nullable=False),
    sa.Column('periodRegularity', sa.String(length=50), nullable=False),
    sa.Column('periodDuration', sa.String(length=50), nullable=False),
    sa.Column('heavyBleeding', sa.String(length=50), nullable=False),
    sa.Column('severeCramps', sa.String(length=50), nullable=False),
    sa.Column('pcosDiagnosis', sa.String(length=50), nullable=False),
    sa.Column('hirsutism', sa.String(length=50), nullable=False),
    sa.Column('hairLoss', sa.String(length=50), nullable=False),
    sa.Column('acneSkinIssues', sa.String(length=50), nullable=False),
    sa.Column('weightGain', sa.String(length=50), nullable=False),
    sa.Column('fatigue', sa.String(length=50), nullable=False),
    sa.Column('exerciseFrequency', sa.String(length=50), nullable=False),
    sa.Column('dietType', sa.String(length=50), nullable=False),
    sa.Column('processedFoodConsumption', sa.String(length=50), nullable=False),
    sa.Column('sugarCravings', sa.String(length=50), nullable=False),
    sa.Column('waterIntake', sa.String(length=50), nullable=False),
    sa.Column('sleepHours', sa.String(length=50), nullable=False),
    sa.Column('sleepDisturbances', sa.String(length=50), nullable=False),
    sa.Column('mentalHealthIssues', sa.String(length=50), nullable=False),
    sa.Column('stressLevels', sa.String(length=50), nullable=False),
    sa.Column('medicalHistory', sa.String(length=255), nullable=True),
    sa.Column('medications', sa.String(length=255), nullable=True),
    sa.Column('fertilityTreatments', sa.String(length=255), nullable=True),
    sa.Column('createdAt', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('chat_id', sa.String(length=36), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sent_by', sa.Enum('USER', 'AI', name='sendertype'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    op.drop_table('user_detail')
    op.drop_table('chat')
    op.drop_table('user')
    # ### end Alembic commands ###
