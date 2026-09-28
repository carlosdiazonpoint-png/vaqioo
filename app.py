from flask import Flask, render_template
from flask_login import login_required, current_user
from flask_migrate import Migrate

from config import Config
from extensions import db, login_manager, bcrypt
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)

    from routes.auth import auth_bp
    from routes.wallet import wallet_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(wallet_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.route("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
