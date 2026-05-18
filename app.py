import os
import tempfile

from flask import Flask

from data_models import db
from routes import main


def _database_uri():
    configured_uri = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if configured_uri:
        configured_uri = configured_uri.strip()
        if configured_uri in {"postgres://...", "postgresql://..."}:
            raise RuntimeError("DATABASE_URL must be a real Postgres connection string, not a placeholder.")
        if configured_uri.startswith("postgres://"):
            return configured_uri.replace("postgres://", "postgresql+psycopg://", 1)
        if configured_uri.startswith("postgresql://"):
            return configured_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        return configured_uri

    if os.environ.get("VERCEL"):
        return f"sqlite:///{os.path.join(tempfile.gettempdir(), 'library.sqlite')}"

    basedir = os.path.abspath(os.path.dirname(__file__))
    return f"sqlite:///{os.path.join(basedir, 'library.sqlite')}"


def _secret_key():
    configured_key = os.environ.get("SECRET_KEY")
    if configured_key:
        return configured_key

    if os.environ.get("VERCEL") or os.environ.get("FLASK_ENV") == "production":
        raise RuntimeError("SECRET_KEY must be set in production.")

    return "mysecretkey"


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = _secret_key()

    app.config["SQLALCHEMY_DATABASE_URI"] = _database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.update(test_config or {})

    db.init_app(app)
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=True, port=port)
