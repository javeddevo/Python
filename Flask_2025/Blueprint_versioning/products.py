from flask import Flask, jsonify, Blueprint
product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    return jsonify({"id": 1, "name": "Laptop", "price": 1500.00, "stock": 50})

