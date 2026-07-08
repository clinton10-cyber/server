"""
Run this once after setting up the database to create an admin user
and a starter set of categories.

Usage: python seed.py
"""
from app import create_app, db
from app.models.user import User, ROLE_ADMIN
from app.models.article import Category
from app.models.page import Page

app = create_app()

CATEGORIES = [
    ("AI", "ai", "Artificial intelligence news and tutorials"),
    ("Programming", "programming", "Coding tutorials and best practices"),
    ("Cybersecurity", "cybersecurity", "Security news and guides"),
    ("Web Development", "web-development", "Frontend and backend web dev"),
    ("Startups", "startups", "Tech startup news"),
    ("Mobile Technology", "mobile-technology", "Mobile dev and news"),
]

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@clinton.tech").first():
        admin = User(username="admin", email="admin@clinton.tech", role=ROLE_ADMIN)
        admin.set_password("changeme123")
        db.session.add(admin)
        print("Created admin user: admin@clinton.tech / changeme123")
    else:
        print("Admin user already exists.")

    for name, slug, desc in CATEGORIES:
        if not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(name=name, slug=slug, description=desc))

    if not Page.query.filter_by(slug="privacy-policy").first():
        db.session.add(
            Page(
                title="Privacy Policy",
                slug="privacy-policy",
                content=(
                    "<p>This page describes how Clinton Tech uses cookies, "
                    "Google AdSense, and (if enabled) Mellowtel to support the "
                    "site. Replace this placeholder with your actual policy "
                    "before going live.</p>"
                ),
                show_in_nav=False,
            )
        )

    db.session.commit()
    print("Seeding complete.")
