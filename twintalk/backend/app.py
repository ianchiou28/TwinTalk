"""Digital Twin Backend — Flask application entry point."""

import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from config import get_config
from database import init_db, get_db
from models.questionnaire import Questionnaire
from api import register_blueprints

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory."""
    config = get_config()

    app = Flask(__name__)
    app.config.from_object(config)

    # 1. 安全中间件：全范围添加安全 HTTP 头 (防止 XSS, Clickjacking)
    Talisman(
        app,
        force_https=not config.DEBUG,  # 生产环境强制转 HTTPS
        content_security_policy={
            'default-src': ["'self'"],
        }
    )

    # 2. 安全配置：严格控制 CORS, 代替原本的 "*"
    CORS(app, resources={r"/api/*": {"origins": config.ALLOWED_ORIGINS}})

    # 3. 流量控制：防刷接口 (Rate Limiting)，以 IP 访问地址为限
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[config.RATELIMIT_DEFAULT],
        storage_uri="memory://" 
    )

    # Initialize database
    init_db(config.DATABASE_URL)
    logger.info(f"Database initialized: {config.DATABASE_URL}")
    
    # Seed initial questionnaires if needed
    from seed_data import seed_questionnaires
    db = get_db()
    try:
        if db.query(Questionnaire).count() == 0:
            logger.info("Seeding initial questionnaires...")
            seed_questionnaires(db)
            db.commit()
            logger.info("✓ Questionnaires seeded successfully")
    except Exception as e:
        logger.error(f"Failed to seed questionnaires: {e}")
    finally:
        db.close()

    # Register API blueprints
    register_blueprints(app)
    logger.info("API blueprints registered")

    # 4. 全局异常抓取：防止堆栈泄露给前端 (Security Info Disclosure Prevention)
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            # 允许已知的 Http 错误状态码
            return jsonify(error=e.name, description=e.description), e.code
        
        # 记录内部错误到日志
        logger.error(f"Server Error: {str(e)}")
        # 对外永远只讲：内部错误
        return jsonify(error="Internal Server Error", description="An unexpected error has occurred."), 500

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "twintalk-backend"}

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    config = get_config()
    logger.info(f"Starting Digital Twin backend on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
