"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create competitors table
    op.create_table(
        'competitors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('country', sa.String(2), default='PE'),
        sa.Column('website_driver', sa.String(500)),
        sa.Column('website_rider', sa.String(500)),
        sa.Column('appstore_id', sa.String(100)),
        sa.Column('playstore_id', sa.String(100)),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('name_ru', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100)),
        sa.Column('name_es', sa.String(100)),
    )
    
    # Create driver_tariffs table
    op.create_table(
        'driver_tariffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('competitor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('commission_rate', sa.Numeric(5, 2)),
        sa.Column('min_fare', sa.Numeric(10, 2)),
        sa.Column('signup_bonus', sa.Numeric(10, 2)),
        sa.Column('referral_bonus', sa.Numeric(10, 2)),
        sa.Column('requirements', postgresql.ARRAY(sa.String)),
        sa.Column('benefits', postgresql.ARRAY(sa.String)),
        sa.Column('currency', sa.String(3), default='PEN'),
        sa.Column('source_url', sa.String(500)),
        sa.Column('is_latest', sa.Boolean, default=True),
        sa.Column('collected_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('idx_driver_tariffs_latest', 'driver_tariffs', ['competitor_id'], postgresql_where=sa.text('is_latest = true'))
    
    # Create rider_tariffs table
    op.create_table(
        'rider_tariffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('competitor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_type', sa.String(50), default='standard'),
        sa.Column('base_fare', sa.Numeric(10, 2)),
        sa.Column('per_km_rate', sa.Numeric(10, 2)),
        sa.Column('per_min_rate', sa.Numeric(10, 2)),
        sa.Column('booking_fee', sa.Numeric(10, 2)),
        sa.Column('currency', sa.String(3), default='PEN'),
        sa.Column('source_url', sa.String(500)),
        sa.Column('is_latest', sa.Boolean, default=True),
        sa.Column('collected_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Create promos table
    op.create_table(
        'promos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('competitor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200)),
        sa.Column('description', sa.Text),
        sa.Column('code', sa.String(50)),
        sa.Column('discount_type', sa.String(20)),
        sa.Column('discount_value', sa.Numeric(10, 2)),
        sa.Column('valid_from', sa.Date),
        sa.Column('valid_until', sa.Date),
        sa.Column('conditions', sa.Text),
        sa.Column('target_audience', sa.String(20), default='rider'),
        sa.Column('source_url', sa.String(500)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('collected_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Create releases table
    op.create_table(
        'releases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('competitor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(20), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('release_date', sa.Date),
        sa.Column('release_notes', sa.Text),
        sa.Column('rating', sa.Numeric(2, 1)),
        sa.Column('rating_count', sa.Integer),
        sa.Column('significance', sa.String(20)),
        sa.Column('summary_ru', sa.Text),
        sa.Column('collected_at', sa.DateTime, default=sa.func.now()),
        sa.UniqueConstraint('competitor_id', 'platform', 'version', name='uq_release_version'),
    )
    
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('external_id', sa.String(100), unique=True, nullable=False),
        sa.Column('competitor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(20), nullable=False),
        sa.Column('author', sa.String(200)),
        sa.Column('rating', sa.SmallInteger, nullable=False),
        sa.Column('text', sa.Text),
        sa.Column('review_date', sa.Date),
        sa.Column('app_version', sa.String(20)),
        sa.Column('language', sa.String(5), default='es'),
        sa.Column('role', sa.String(20), default='unknown'),
        sa.Column('sentiment', sa.String(20)),
        sa.Column('key_topics', sa.Text),
        sa.Column('collected_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('idx_reviews_competitor', 'reviews', ['competitor_id'])
    op.create_index('idx_reviews_date', 'reviews', ['review_date'])
    op.create_index('idx_reviews_sentiment', 'reviews', ['sentiment'])
    op.create_index('idx_reviews_role', 'reviews', ['role'])
    
    # Create collection_logs table
    op.create_table(
        'collection_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_type', sa.String(20), nullable=False),
        sa.Column('competitor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competitors.id', ondelete='SET NULL')),
        sa.Column('task_name', sa.String(100)),
        sa.Column('url', sa.String(500)),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text),
        sa.Column('items_collected', sa.Integer, default=0),
        sa.Column('raw_payload', postgresql.JSONB),
        sa.Column('started_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Create digests table
    op.create_table(
        'digests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('period_start', sa.Date, nullable=False),
        sa.Column('period_end', sa.Date, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_by', sa.String(100)),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Create news_items table
    op.create_table(
        'news_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('search_query', sa.Text, nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text),
        sa.Column('content', sa.Text),
        sa.Column('source_url', sa.String(1000)),
        sa.Column('source_name', sa.String(200)),
        sa.Column('source_type', sa.String(20), nullable=False),
        sa.Column('published_date', sa.Date),
        sa.Column('language', sa.String(5), default='es'),
        sa.Column('competitors_mentioned', postgresql.ARRAY(sa.String)),
        sa.Column('topics', postgresql.ARRAY(sa.String)),
        sa.Column('sentiment', sa.String(20)),
        sa.Column('relevance_score', sa.Float),
        sa.Column('raw_response', postgresql.JSONB),
        sa.Column('is_processed', sa.Boolean, default=False),
        sa.Column('is_relevant', sa.Boolean, default=True),
        sa.Column('collected_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('idx_news_items_date', 'news_items', ['published_date'])
    op.create_index('idx_news_items_relevant', 'news_items', ['is_relevant'])
    
    # Insert initial data
    op.execute("""
        INSERT INTO competitors (id, name, slug, website_driver, website_rider, appstore_id, playstore_id) VALUES
        (gen_random_uuid(), 'InDriver', 'indriver', 'https://indriver.com/pe/driver', 'https://indriver.com/pe', 'id1018263498', 'sinet.startup.inDriver'),
        (gen_random_uuid(), 'Didi', 'didi', 'https://web.didiglobal.com/pe/driver', 'https://web.didiglobal.com/pe', 'id1447432993', 'com.xiaojukeji.didi.global.customer'),
        (gen_random_uuid(), 'Uber', 'uber', 'https://www.uber.com/pe/es/drive', 'https://www.uber.com/pe/es', 'id368677368', 'com.ubercab'),
        (gen_random_uuid(), 'Cabify', 'cabify', 'https://cabify.com/pe/driver', 'https://cabify.com/pe', 'id476087442', 'com.cabify.rider')
    """)
    
    op.execute("""
        INSERT INTO categories (slug, name_ru, name_en, name_es) VALUES
        ('pricing', 'Тарифы', 'Pricing', 'Tarifas'),
        ('ux_ui', 'UX/UI', 'UX/UI', 'UX/UI'),
        ('safety', 'Безопасность', 'Safety', 'Seguridad'),
        ('driver_exp', 'Опыт водителя', 'Driver Experience', 'Experiencia conductor'),
        ('rider_exp', 'Опыт пассажира', 'Rider Experience', 'Experiencia pasajero'),
        ('promo', 'Промо', 'Promo', 'Promoción'),
        ('support', 'Поддержка', 'Support', 'Soporte'),
        ('payment', 'Оплата', 'Payment', 'Pago'),
        ('wait_time', 'Время ожидания', 'Wait Time', 'Tiempo de espera'),
        ('other', 'Другое', 'Other', 'Otro')
    """)


def downgrade() -> None:
    op.drop_table('news_items')
    op.drop_table('digests')
    op.drop_table('collection_logs')
    op.drop_table('reviews')
    op.drop_table('releases')
    op.drop_table('promos')
    op.drop_table('rider_tariffs')
    op.drop_table('driver_tariffs')
    op.drop_table('categories')
    op.drop_table('competitors')

