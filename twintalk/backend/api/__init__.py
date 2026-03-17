"""API package — register all blueprints."""

from .auth import auth_bp
from .questionnaire import questionnaire_bp
from .profile import profile_bp
from .chat import chat_bp
from .social import social_bp
from .memory import memory_bp


def register_blueprints(app):
    """Register all API blueprints with the Flask app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(questionnaire_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(memory_bp)


__all__ = [
    "auth_bp", "questionnaire_bp", "profile_bp", "chat_bp", "social_bp",
    "memory_bp", "register_blueprints",
]
