from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.article import Article, Category
from app.models.page import Page
from app.models.user import User
from app.models.ad import Ad
from app.models.media import Media
from app.models.settings import SiteSetting

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_author:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_articles": Article.query.count(),
        "published_articles": Article.query.filter_by(status="published").count(),
        "draft_articles": Article.query.filter_by(status="draft").count(),
        "total_users": User.query.count(),
        "total_pages": Page.query.count(),
    }
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats, recent_articles=recent_articles)


@admin_bp.route("/articles")
@login_required
@admin_required
def articles_list():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template("admin/articles_list.html", articles=articles)


@admin_bp.route("/articles/new", methods=["GET", "POST"])
@login_required
@admin_required
def article_new():
    categories = Category.query.all()
    if request.method == "POST":
        from slugify import slugify
        from app.models.article import Tag

        title = request.form.get("title", "").strip()
        article = Article(
            title=title,
            slug=slugify(title),
            summary=request.form.get("summary"),
            content=request.form.get("content"),
            status=request.form.get("status", "draft"),
            category_id=request.form.get("category_id") or None,
            author_id=current_user.id,
            seo_title=request.form.get("seo_title") or title,
            seo_description=request.form.get("seo_description") or request.form.get("summary"),
        )

        db.session.add(article)

        tag_names = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        for name in tag_names:
            tag_slug = slugify(name)
            tag = Tag.query.filter_by(slug=tag_slug).first()
            if not tag:
                tag = Tag(name=name, slug=tag_slug)
                db.session.add(tag)
            article.tags.append(tag)

        if article.status == "published":
            from datetime import datetime

            article.published_at = datetime.utcnow()

        db.session.commit()
        flash("Article created.", "success")
        return redirect(url_for("admin.articles_list"))

    return render_template("admin/article_form.html", categories=categories, article=None)


@admin_bp.route("/pages")
@login_required
@admin_required
def pages_list():
    pages = Page.query.order_by(Page.created_at.desc()).all()
    return render_template("admin/pages_list.html", pages=pages)


@admin_bp.route("/pages/new", methods=["GET", "POST"])
@login_required
@admin_required
def page_new():
    if request.method == "POST":
        from slugify import slugify

        title = request.form.get("title", "").strip()
        page = Page(
            title=title,
            slug=slugify(title),
            content=request.form.get("content"),
            show_in_nav=bool(request.form.get("show_in_nav")),
            seo_title=request.form.get("seo_title") or title,
            seo_description=request.form.get("seo_description"),
        )
        db.session.add(page)
        db.session.commit()
        flash("Page created.", "success")
        return redirect(url_for("admin.pages_list"))

    return render_template("admin/page_form.html", page=None)


@admin_bp.route("/users")
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users_list.html", users=users)


@admin_bp.route("/users/<int:user_id>/ban", methods=["POST"])
@login_required
@admin_required
def ban_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    user.is_banned = not user.is_banned
    db.session.commit()
    flash(f"User {'banned' if user.is_banned else 'unbanned'}.", "success")
    return redirect(url_for("admin.users_list"))


# --- Ads / Monetization -----------------------------------------------

AD_PLACEMENTS = [
    "homepage_top",
    "homepage_sidebar",
    "article_inline",
    "article_bottom",
]


@admin_bp.route("/ads")
@login_required
@admin_required
def ads_list():
    if not current_user.is_admin:
        abort(403)
    ads = Ad.query.order_by(Ad.placement, Ad.priority.desc()).all()
    return render_template("admin/ads_list.html", ads=ads)


@admin_bp.route("/ads/new", methods=["GET", "POST"])
@login_required
@admin_required
def ad_new():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        ad = Ad(
            name=request.form.get("name", "").strip(),
            placement=request.form.get("placement"),
            ad_type=request.form.get("ad_type", "html"),
            html_snippet=request.form.get("html_snippet") or None,
            image_url=request.form.get("image_url") or None,
            link_url=request.form.get("link_url") or None,
            priority=int(request.form.get("priority") or 0),
            is_active=bool(request.form.get("is_active")),
        )
        db.session.add(ad)
        db.session.commit()
        flash("Ad created.", "success")
        return redirect(url_for("admin.ads_list"))

    return render_template("admin/ad_form.html", ad=None, placements=AD_PLACEMENTS)


@admin_bp.route("/ads/<int:ad_id>/toggle", methods=["POST"])
@login_required
@admin_required
def ad_toggle(ad_id):
    if not current_user.is_admin:
        abort(403)
    ad = Ad.query.get_or_404(ad_id)
    ad.is_active = not ad.is_active
    db.session.commit()
    flash(f"Ad {'activated' if ad.is_active else 'paused'}.", "success")
    return redirect(url_for("admin.ads_list"))


@admin_bp.route("/ads/<int:ad_id>/delete", methods=["POST"])
@login_required
@admin_required
def ad_delete(ad_id):
    if not current_user.is_admin:
        abort(403)
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    flash("Ad deleted.", "success")
    return redirect(url_for("admin.ads_list"))


@admin_bp.route("/settings/monetization")
@login_required
@admin_required
def monetization_settings():
    """Read-only view showing current env-driven AdSense/Mellowtel config,
    since those keys live in .env (not the DB) and require a server restart
    to change."""
    if not current_user.is_admin:
        abort(403)
    from flask import current_app

    return render_template(
        "admin/monetization_settings.html",
        adsense_client_id=current_app.config.get("GOOGLE_ADSENSE_CLIENT_ID"),
        mellowtel_config_uuid=current_app.config.get("MELLOWTEL_CONFIG_UUID"),
    )


@admin_bp.route("/settings/general", methods=["GET", "POST"])
@login_required
@admin_required
def general_settings():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        SiteSetting.set("whatsapp_group_link", request.form.get("whatsapp_group_link", "").strip())
        flash("Settings saved.", "success")
        return redirect(url_for("admin.general_settings"))

    whatsapp_group_link = SiteSetting.get("whatsapp_group_link", "")
    return render_template("admin/general_settings.html", whatsapp_group_link=whatsapp_group_link)


@admin_bp.route("/upload-image", methods=["POST"])
@login_required
@admin_required
def upload_image():
    """Image upload endpoint used by the rich text editor (Quill) in the
    article/page admin forms. Returns {"url": "..."} for the editor to embed."""
    import os
    import uuid
    from flask import current_app, jsonify

    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file provided"}), 400

    allowed_ext = {"png", "jpg", "jpeg", "gif", "webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed_ext:
        return jsonify({"error": "Unsupported file type"}), 400

    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    media = Media(
        filename=filename,
        filepath=f"/static/uploads/{filename}",
        file_type="image",
        uploaded_by=current_user.id,
    )
    db.session.add(media)
    db.session.commit()

    return jsonify({"url": url_for("static", filename=f"uploads/{filename}")})
