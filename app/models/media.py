from datetime import datetime
from app import db


class Media(db.Model):
    __tablename__ = "media"
    __bind_key__ = "media"  # lives in a separate database, see MEDIA_DATABASE_URL

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    filepath = db.Column(db.String(400), nullable=False)
    file_type = db.Column(db.String(30))  # image, video, pdf, zip, document
    folder = db.Column(db.String(120), default="general")
    uploaded_by = db.Column(db.Integer)  # references users.id, but no FK constraint since
    # this table lives in a separate database (cross-database FKs aren't supported)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Media {self.filename}>"
