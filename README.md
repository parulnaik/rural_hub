# Rural Hub

Rural Hub is a digital platform connecting rural users, scrap dealers, and local service providers. It facilitates transparent scrap bidding, local service booking, and a cashless barter exchange.

## Features
- **Scrap Bidding**: List scrap, accept bids from verified dealers.
- **Service Booking**: Find and book local services (tractor repair, plumbing, etc.).
- **Barter Marketplace**: Exchange goods and services directly with neighbors.
- **Role-based Dashboards**: Custom views for users, dealers, service providers, and admins.

## Tech Stack
- **Backend**: Python Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML5, Vanilla CSS, Jinja2
- **Image Storage**: Cloudinary (Vercel-compatible)
- **Deployment**: Vercel

---

## Local Development Setup

1. **Clone the repository** and navigate to the project directory:
   ```bash
   cd rural_hub
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Copy the `.env.example` file to a new file named `.env` and fill in the values:
   ```bash
   copy .env.example .env
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

5. **Health check**:
   ```bash
   http://127.0.0.1:5000/health
   ```

6. **Run tests**:
   ```bash
   .\.venv\Scripts\python.exe -m unittest discover -s tests -v
   ```

---

## Production / Vercel Notes

- This project is designed to use PostgreSQL via `DATABASE_URL` in production.
- Cloudinary is used for persistent uploads.
- The app exposes a health endpoint at `/health` for deployment monitoring.
- The production entry point remains `run.py`, and the `vercel.json` layer routes all requests there.
- Local SQLite is used when `DATABASE_URL` is not configured. A configured but unreachable PostgreSQL database causes startup to fail rather than silently switching databases.

### Required configuration variables
- `SECRET_KEY`
- `DATABASE_URL`
- `CLOUDINARY_URL`

For Supabase, copy the connection URI from **Project → Connect** into `DATABASE_URL` in `.env`. Use the **Session pooler** URI if your network does not support Supabase's direct IPv6 database endpoint. In Vercel, add the same value under **Project → Settings → Environment Variables** instead of relying on the local `.env` file.

Optional values:
- `AI_API_KEY`
- `AI_PROVIDER`
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `PUBLIC_BASE_URL`

### Vercel deployment checklist
1. Push the repository to GitHub.
2. Import it into Vercel.
3. Add the environment variables shown in `.env.example`.
4. Deploy.
5. Confirm the app responds on `/health` after deployment.

> Important: do not commit real secrets. Use Vercel environment variables only.
