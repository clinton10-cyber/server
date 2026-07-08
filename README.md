# Clinton Tech — Phase 1 Foundation

Flask + PostgreSQL scaffold for the Clinton Tech platform. This is Phase 1
of the full build: core architecture, auth, base models, homepage, and a
working admin dashboard.

## What's included

- App factory pattern (`app/__init__.py`)
- Models: User (roles: admin/author/user), Article, Category, Tag, Page,
  Comment, Media
- Auth: register/login/logout (Flask-Login, hashed passwords)
- Public site: homepage (trending/latest/featured), article detail,
  category pages, dynamic page rendering
- Admin dashboard: stats, article CRUD (create), page CRUD (create),
  user management (list + ban/unban), role-protected routes
- Light/dark mode toggle (persisted via localStorage)
- Responsive base CSS

## Setup

1. Create a PostgreSQL database:
   ```
   createdb clinton_tech
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update `DATABASE_URL` / `SECRET_KEY`.

4. Seed the database (creates tables + an admin user + starter categories):
   ```
   python seed.py
   ```
   Default admin login: `admin@clinton.tech` / `changeme123` — change this
   immediately.

5. Run the app:
   ```
   python run.py
   ```
   Visit `http://localhost:5000`. Admin panel at `/admin` (login as admin
   first).

## Deploying on Render

1. Push this project to a GitHub repo.
2. In Render: New → Blueprint → connect the repo. `render.yaml` (included)
   auto-configures a web service + free PostgreSQL database.
3. Or manually: New → Web Service → connect repo →
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn run:app`
   - Add a PostgreSQL instance and set `DATABASE_URL` to its connection string
   - Set `SECRET_KEY`, and optionally `GOOGLE_ADSENSE_CLIENT_ID` / `MELLOWTEL_CONFIG_UUID`
4. After first deploy, run the seed script once via Render's Shell tab:
   ```
   python seed.py
   ```
5. Change the default admin password immediately after first login.

Note: Render's free Postgres instances expire after 90 days unless upgraded.



- Phase 2: full article editor (rich text, images, code snippets, tags UI),
  page builder UI, homepage sections wired to real data
- Phase 3: scheduling/drafts UI, analytics charts
- Phase 4: tutorials hub, coding challenges, comments/likes/bookmarks
- Phase 5: resource library, AI tools directory, full-text search, media
  library UI
- Phase 6: newsletter, SEO automation, monetization
- Phase 7: courses, job board, marketplace, API

Send me a message when you're ready for the next phase and I'll build on
top of this foundation.

## Phase 2 additions (this round)

- Rich text/image editor (Quill) on article & page admin forms — images upload to `/admin/upload-image` and embed inline
- Tags UI on article form (comma-separated, auto-created), tag pages at `/tag/<slug>`
- Comments, likes, bookmarks (per-user, login required) on articles
- Basic search (`/search?q=...`) across title/summary/content
- SEO meta tags (title, description, Open Graph) rendered per article/page
- Dynamic pages share one template — only content differs per page; pages marked "show in nav" appear in the header automatically
- WhatsApp community join button in header, link set via `/admin/settings/general` (stored in DB, editable without a restart)
- Confirmed Supabase/Postgres interchangeability via `DATABASE_URL` — no code changes needed either way

## Still pending (next phase)

- Tutorials hub, coding challenges, resource library, AI tools directory, newsletter system, SEO automation (sitemap/robots.txt/structured data), courses/job board/marketplace

## Two databases: content vs. media

- `DATABASE_URL` — main content database (users, articles, pages, comments, ads, settings, etc.)
- `MEDIA_DATABASE_URL` — separate database for the `media` table (uploaded image metadata/paths). If left blank, media falls back to living in `DATABASE_URL` (single-database mode).
- `seed.py`'s `db.create_all()` creates tables in both databases automatically based on each model's `__bind_key__`.
- Note: since media lives in a different database, `Media.uploaded_by` is a plain integer (not an enforced foreign key) — cross-database FK constraints aren't supported in Postgres.
- This can point at two different providers too — e.g. content on Supabase, media on a separate Postgres instance — since each URL is independent.
