from datetime import datetime
from app import db


class Like(db.Model):
    __tablename__ = "likes"
    __table_args__ = (db.UniqueConstraint("user_id", "article_id", name="uq_like_user_article"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    __table_args__ = (db.UniqueConstraint("user_id", "article_id", name="uq_bookmark_user_article"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
