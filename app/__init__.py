import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clinton_tech"
    )
    app.config["SQLALCHEMY_BINDS"] = {
        "media": os.environ.get("MEDIA_DATABASE_URL") or os.environ.get(
            "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clinton_tech"
        )
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")

    # Monetization / third-party scripts (gated behind cookie consent, see base.html)
    app.config["GOOGLE_ADSENSE_CLIENT_ID"] = os.environ.get("GOOGLE_ADSENSE_CLIENT_ID", "")
    app.config["MELLOWTEL_CONFIG_UUID"] = os.environ.get("MELLOWTEL_CONFIG_UUID", "")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    migrate.init_app(app, db)

    from app.models import user, article, page, comment, media, ad, settings, engagement  # noqa

    # The "media" bind lives in a separate physical database (MEDIA_DATABASE_URL)
    # and isn't tracked by Alembic migrations, since it's a single simple table.
    # This creates it automatically if it doesn't exist yet — safe/idempotent
    # to run on every startup.
    with app.app_context():
        db.create_all(bind_key="media")

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(pages_bp)

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {
            "current_year": datetime.utcnow().year,
            "adsense_client_id": app.config["GOOGLE_ADSENSE_CLIENT_ID"],
            "mellowtel_config_uuid": app.config["MELLOWTEL_CONFIG_UUID"],
        }

    @app.context_processor
    def inject_ad_helper():
        from app.models.ad import Ad

        def get_ads(placement):
            return (
                Ad.query.filter_by(placement=placement, is_active=True)
                .order_by(Ad.priority.desc())
                .all()
            )

        return {"get_ads": get_ads}

    @app.context_processor
    def inject_site_settings():
        from app.models.settings import SiteSetting

        return {"whatsapp_group_link": SiteSetting.get("whatsapp_group_link", "")}

    @app.context_processor
    def inject_nav_pages():
        from app.models.page import Page

        return {
            "nav_pages": Page.query.filter_by(is_published=True, show_in_nav=True)
            .order_by(Page.nav_order)
            .all()
        }

    @app.context_processor
    def inject_engagement_helpers():
        from flask_login import current_user
        from app.models.engagement import Like, Bookmark

        def has_liked(article_id):
            if not current_user.is_authenticated:
                return False
            return Like.query.filter_by(user_id=current_user.id, article_id=article_id).first() is not None

        def has_bookmarked(article_id):
            if not current_user.is_authenticated:
                return False
            return Bookmark.query.filter_by(user_id=current_user.id, article_id=article_id).first() is not None

        return {"has_liked": has_liked, "has_bookmarked": has_bookmarked}

    return app
