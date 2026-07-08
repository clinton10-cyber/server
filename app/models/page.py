from datetime import datetime
from app import db


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)  # rendered HTML from page builder / rich text editor
    is_published = db.Column(db.Boolean, default=True)

    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))

    show_in_nav = db.Column(db.Boolean, default=False)
    nav_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Page {self.title}>"
