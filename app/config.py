import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dotenv import load_dotenv

# Load .env from the project root even when the app is started from another working directory.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(BASE_DIR, '.env'))


def normalize_database_url(raw_url):
    if not raw_url:
        return 'sqlite:///local_dev.db'

    url = raw_url.strip()
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        return 'sqlite:///local_dev.db'

    if parsed.hostname and (
        parsed.hostname.endswith('.supabase.co')
        or parsed.hostname.endswith('.supabase.com')
        or '.pooler.supabase.com' in parsed.hostname
    ):
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query.setdefault('sslmode', 'require')
        parsed = parsed._replace(query=urlencode(query))
        return parsed.geturl()

    return url


class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = bool(os.environ.get('VERCEL'))
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = bool(os.environ.get('VERCEL'))

    # Database config
    if os.environ.get('VERCEL'):
        default_db = 'sqlite:////tmp/local_dev.db'
    else:
        default_db = 'sqlite:///local_dev.db'

    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.environ.get('DATABASE_URL', default_db))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cloudinary Config
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
