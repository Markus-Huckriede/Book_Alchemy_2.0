import os

from flask import Flask

from data_models import db
from routes import main


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "mysecretkey")

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'library.sqlite')}"
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
