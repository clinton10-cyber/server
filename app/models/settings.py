from app import db


class SiteSetting(db.Model):
    """
    Simple key-value settings store, editable from the admin panel.
    Works identically whether DATABASE_URL points at Supabase or a plain
    Postgres instance — it's just a table.
    """

    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)

    @staticmethod
    def get(key, default=""):
        row = SiteSetting.query.filter_by(key=key).first()
        return row.value if row and row.value else default

    @staticmethod
    def set(key, value):
        row = SiteSetting.query.filter_by(key=key).first()
        if row:
            row.value = value
        else:
            row = SiteSetting(key=key, value=value)
            db.session.add(row)
        db.session.commit()
