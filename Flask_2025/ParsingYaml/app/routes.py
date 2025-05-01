from flask import Blueprint, request, jsonify
from . import db
from .models import Order
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        category = request.args.get('category')
        price = request.args.get('price')

        query = Order.query

        if category:
            query = query.filter_by(category=category)
        if price:
            try:
                query = query.filter(Order.price <= float(price))
            except ValueError:
                logger.error("Invalid price parameter")
                return jsonify({"error": "Price must be a valid number"}), 400

        orders = query.all()
        logger.info(f"Retrieved {len(orders)} orders")
        return jsonify([order.to_dict() for order in orders])
    except Exception as e:
        logger.error(f"Error retrieving orders: {str(e)}")
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/orders', methods=['POST'])
def add_orders():
    try:
        orders_data = request.json
        if not isinstance(orders_data, list):
            logger.error("Request body must be a list")
            return jsonify({"error": "Request body must be a list of orders"}), 400

        added_count = 0
        for order_data in orders_data:
            if not all(key in order_data for key in ['name', 'purchased_date', 'price', 'category']):
                logger.error("Missing required fields in order data")
                return jsonify({"error": "Missing required fields in order data"}), 400

            additional_data = order_data.get('additional_data', {})
            dimensions = additional_data.get('dimensions', {}) or {}

            order = Order(
                name=order_data['name'],
                purchased_date=order_data['purchased_date'],
                price=order_data['price'],
                category=order_data['category'],
                expiration=additional_data.get('expiration'),
                dimensions_length=dimensions.get('length'),
                dimensions_width=dimensions.get('width'),
                dimensions_depth=dimensions.get('depth')
            )
            db.session.add(order)
            added_count += 1

        db.session.commit()
        logger.info(f"Added {added_count} orders")
        return jsonify({"message": f"{added_count} orders added successfully"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding orders: {str(e)}")
        return jsonify({"error": str(e)}), 400