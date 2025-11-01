"""Application factory for the Password-less chat app."""
from __future__ import annotations

from datetime import datetime

from flask import Flask, Response

from .config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from .extensions import csrf, db, limiter, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    config_obj = _select_config(config_name)
    app.config.from_object(config_obj)

    _register_extensions(app)
    _register_blueprints(app)
    _register_cli(app)
    _register_error_handlers(app)
    _register_security_headers(app)
    _register_template_context(app)

    return app


def _select_config(config_name: str | None) -> type[Config]:
    env = config_name or app_env()
    mapping = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    return mapping.get(env, Config)


def app_env() -> str:
    from os import getenv

    return getenv("FLASK_ENV", "development")


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    limiter.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:  # pragma: no cover - simple accessor
        return User.query.get(int(user_id))


def _register_blueprints(app: Flask) -> None:
    from .auth.routes import bp as auth_bp
    from .chat.routes import bp as chat_bp
    from .main.routes import bp as main_bp
    from .admin.routes import bp as admin_bp
    from .face_placeholder.routes import bp as face_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(face_bp, url_prefix="/face")


def _register_cli(app: Flask) -> None:
    from . import cli

    app.cli.add_command(cli.create_admin)
    app.cli.add_command(cli.list_users)
    app.cli.add_command(cli.clear_messages)


def _register_error_handlers(app: Flask) -> None:
    from flask import render_template

    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple[str, int]:
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error: Exception) -> tuple[str, int]:
        return render_template("errors/404.html"), 500


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def set_secure_headers(response: Response) -> Response:
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:;",
        )
        return response


def _register_template_context(app: Flask) -> None:
    @app.context_processor
    def inject_globals():  # pragma: no cover - simple helper
        return {"current_year": datetime.utcnow().year}


app = create_app()
