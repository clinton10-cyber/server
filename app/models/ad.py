from datetime import datetime
from app import db


class Ad(db.Model):
    """
    Admin-managed ad slot. Supports either:
    - raw HTML/JS snippet (e.g. an AdSense <ins> unit, a sponsored banner), or
    - a simple image + link (sponsored post style banner)
    placed into a named position on the site (e.g. 'homepage_top',
    'sidebar', 'article_inline').
    """

    __tablename__ = "ads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    placement = db.Column(db.String(80), nullable=False, index=True)
    # e.g. homepage_top, homepage_sidebar, article_inline, article_bottom

    ad_type = db.Column(db.String(30), default="html")  # html, image
    html_snippet = db.Column(db.Text)  # raw HTML/JS (e.g. AdSense unit)

    image_url = db.Column(db.String(400))
    link_url = db.Column(db.String(400))

    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # higher shows first when multiple share a placement

    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Ad {self.name} @ {self.placement}>"
