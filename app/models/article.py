from datetime import datetime
from app import db

article_tags = db.Table(
    "article_tags",
    db.Column("article_id", db.Integer, db.ForeignKey("articles.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    articles = db.relationship("Article", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(400))
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(300))

    status = db.Column(db.String(20), default="draft")  # draft, published, scheduled
    scheduled_for = db.Column(db.DateTime, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)

    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    reading_time_minutes = db.Column(db.Integer, default=1)

    is_featured = db.Column(db.Boolean, default=False)
    is_breaking_news = db.Column(db.Boolean, default=False)

    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    tags = db.relationship("Tag", secondary=article_tags, backref="articles")
    comments = db.relationship("Comment", backref="article", lazy="dynamic", cascade="all, delete-orphan")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Article {self.title}>"
