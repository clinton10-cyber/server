from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.article import Article, Category, Tag
from app.models.comment import Comment
from app.models.engagement import Like, Bookmark

main_bp = Blueprint("main", __name__, template_folder="../templates")


@main_bp.route("/")
def home():
    trending = (
        Article.query.filter_by(status="published")
        .order_by(Article.view_count.desc())
        .limit(5)
        .all()
    )
    latest = (
        Article.query.filter_by(status="published")
        .order_by(Article.published_at.desc())
        .limit(8)
        .all()
    )
    featured = Article.query.filter_by(status="published", is_featured=True).limit(4).all()
    breaking = Article.query.filter_by(status="published", is_breaking_news=True).limit(3).all()
    categories = Category.query.all()

    return render_template(
        "index.html",
        trending=trending,
        latest=latest,
        featured=featured,
        breaking=breaking,
        categories=categories,
    )


@main_bp.route("/article/<slug>")
def article_detail(slug):
    article = Article.query.filter_by(slug=slug, status="published").first_or_404()
    article.view_count = (article.view_count or 0) + 1
    from app import db

    db.session.commit()
    related = (
        Article.query.filter(
            Article.category_id == article.category_id, Article.id != article.id
        )
        .limit(4)
        .all()
    )
    top_level_comments = (
        Comment.query.filter_by(article_id=article.id, parent_id=None)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return render_template(
        "article_detail.html", article=article, related=related, top_level_comments=top_level_comments
    )


@main_bp.route("/category/<slug>")
def category_view(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    articles = (
        Article.query.filter_by(category_id=category.id, status="published")
        .order_by(Article.published_at.desc())
        .all()
    )
    return render_template("category.html", category=category, articles=articles)


@main_bp.route("/tag/<slug>")
def tag_view(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    articles = [a for a in tag.articles if a.status == "published"]
    return render_template("tag.html", tag=tag, articles=articles)


@main_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        like_pattern = f"%{query}%"
        results = (
            Article.query.filter(
                Article.status == "published",
                db.or_(
                    Article.title.ilike(like_pattern),
                    Article.summary.ilike(like_pattern),
                    Article.content.ilike(like_pattern),
                ),
            )
            .order_by(Article.published_at.desc())
            .limit(30)
            .all()
        )
    return render_template("search.html", query=query, results=results)


@main_bp.route("/article/<slug>/comment", methods=["POST"])
@login_required
def add_comment(slug):
    article = Article.query.filter_by(slug=slug, status="published").first_or_404()
    content = request.form.get("content", "").strip()
    if content:
        comment = Comment(content=content, user_id=current_user.id, article_id=article.id)
        db.session.add(comment)
        db.session.commit()
        flash("Comment posted.", "success")
    return redirect(url_for("main.article_detail", slug=slug))


@main_bp.route("/article/<slug>/like", methods=["POST"])
@login_required
def like_article(slug):
    article = Article.query.filter_by(slug=slug, status="published").first_or_404()
    existing = Like.query.filter_by(user_id=current_user.id, article_id=article.id).first()
    if existing:
        db.session.delete(existing)
        article.like_count = max(0, (article.like_count or 0) - 1)
    else:
        db.session.add(Like(user_id=current_user.id, article_id=article.id))
        article.like_count = (article.like_count or 0) + 1
    db.session.commit()
    return redirect(url_for("main.article_detail", slug=slug))


@main_bp.route("/article/<slug>/bookmark", methods=["POST"])
@login_required
def bookmark_article(slug):
    article = Article.query.filter_by(slug=slug, status="published").first_or_404()
    existing = Bookmark.query.filter_by(user_id=current_user.id, article_id=article.id).first()
    if existing:
        db.session.delete(existing)
        flash("Removed from bookmarks.", "success")
    else:
        db.session.add(Bookmark(user_id=current_user.id, article_id=article.id))
        flash("Bookmarked.", "success")
    db.session.commit()
    return redirect(url_for("main.article_detail", slug=slug))


@main_bp.route("/bookmarks")
@login_required
def my_bookmarks():
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).order_by(Bookmark.created_at.desc()).all()
    articles = [Article.query.get(b.article_id) for b in bookmarks]
    return render_template("bookmarks.html", articles=articles)
