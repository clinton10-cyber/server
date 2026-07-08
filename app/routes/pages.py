from flask import Blueprint, render_template
from app.models.page import Page

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/page/<slug>")
def view_page(slug):
    page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("page.html", page=page)
