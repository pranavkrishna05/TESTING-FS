from flask import Flask
from backend.controllers.auth.user_controller import user_bp
from backend.controllers.products.product_controller import product_bp
from backend.controllers.cart.cart_controller import cart_bp
from backend.config.logging_config import setup_logging

def create_app() -> Flask:
    app = Flask(__name__)
    setup_logging()
    app.register_blueprint(user_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)