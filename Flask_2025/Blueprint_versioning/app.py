from flask import Flask
from orders import order_bp
from products import product_bp
from flask_cors import CORS


app=Flask(__name__)

CORS(app)

app.register_blueprint(order_bp, url_prefix='/api/v1')
app.register_blueprint(product_bp, url_prefix='/api/v1')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
# This code sets up a Flask application with two blueprints: one for orders and one for products.
