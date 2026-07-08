"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- users ---
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=300), nullable=True),
        sa.Column('is_banned', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('is_active_account', sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # --- categories ---
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.UniqueConstraint('name', name='uq_categories_name'),
        sa.UniqueConstraint('slug', name='uq_categories_slug'),
    )

    # --- tags ---
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=60), nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.UniqueConstraint('name', name='uq_tags_name'),
        sa.UniqueConstraint('slug', name='uq_tags_slug'),
    )

    # --- pages ---
    op.create_table(
        'pages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=220), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column('seo_title', sa.String(length=200), nullable=True),
        sa.Column('seo_description', sa.String(length=300), nullable=True),
        sa.Column('show_in_nav', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('nav_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('slug', name='uq_pages_slug'),
    )
    op.create_index('ix_pages_slug', 'pages', ['slug'])

    # --- site_settings ---
    op.create_table(
        'site_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.UniqueConstraint('key', name='uq_site_settings_key'),
    )

    # --- ads ---
    op.create_table(
        'ads',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('placement', sa.String(length=80), nullable=False),
        sa.Column('ad_type', sa.String(length=30), nullable=True, server_default='html'),
        sa.Column('html_snippet', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=400), nullable=True),
        sa.Column('link_url', sa.String(length=400), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('impressions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('clicks', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_ads_placement', 'ads', ['placement'])

    # --- articles (depends on users, categories) ---
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=220), nullable=False),
        sa.Column('slug', sa.String(length=250), nullable=False),
        sa.Column('summary', sa.String(length=400), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('featured_image', sa.String(length=300), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('scheduled_for', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('reading_time_minutes', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('is_breaking_news', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('seo_title', sa.String(length=200), nullable=True),
        sa.Column('seo_description', sa.String(length=300), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='fk_articles_author_id_users'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_articles_category_id_categories'),
        sa.UniqueConstraint('slug', name='uq_articles_slug'),
    )
    op.create_index('ix_articles_slug', 'articles', ['slug'])

    # --- article_tags (association table; depends on articles, tags) ---
    op.create_table(
        'article_tags',
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_article_tags_article_id_articles'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name='fk_article_tags_tag_id_tags'),
        sa.PrimaryKeyConstraint('article_id', 'tag_id'),
    )

    # --- comments (depends on users, articles, self-referential) ---
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_comments_user_id_users'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_comments_article_id_articles'),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], name='fk_comments_parent_id_comments'),
    )

    # --- likes (depends on users, articles) ---
    op.create_table(
        'likes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_likes_user_id_users'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_likes_article_id_articles'),
        sa.UniqueConstraint('user_id', 'article_id', name='uq_like_user_article'),
    )

    # --- bookmarks (depends on users, articles) ---
    op.create_table(
        'bookmarks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_bookmarks_user_id_users'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='fk_bookmarks_article_id_articles'),
        sa.UniqueConstraint('user_id', 'article_id', name='uq_bookmark_user_article'),
    )


def downgrade():
    op.drop_table('bookmarks')
    op.drop_table('likes')
    op.drop_table('comments')
    op.drop_table('article_tags')
    op.drop_index('ix_articles_slug', table_name='articles')
    op.drop_table('articles')
    op.drop_index('ix_ads_placement', table_name='ads')
    op.drop_table('ads')
    op.drop_table('site_settings')
    op.drop_index('ix_pages_slug', table_name='pages')
    op.drop_table('pages')
    op.drop_table('tags')
    op.drop_table('categories')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
