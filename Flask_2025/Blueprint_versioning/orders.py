from flask import Flask, request, jsonify,Blueprint
order_bp=Blueprint('order', __name__)

@order_bp.route('/orders', methods=['GET'])
def get_orders():
    return jsonify({"id": 1, "item": "food","order_date": "2023-10-01", "quantity": 2, "total_price": 20.00})




