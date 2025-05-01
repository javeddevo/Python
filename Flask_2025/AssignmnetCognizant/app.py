import os
import yaml
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from datetime import datetime
app = Flask(__name__)

#driver://username:pass@host:port/dbname'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    purchased_date = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=True,default=100.20)
    expiration = db.Column(db.String(20), nullable=True)
    dimensions_length = db.Column(db.Float, nullable=True)
    dimensions_width = db.Column(db.Float, nullable=True)
    dimensions_depth = db.Column(db.Float, nullable=True)

    def to_dict(self):
        dimensions = None
        if any([self.dimensions_length, self.dimensions_width, self.dimensions_depth]):
            dimensions = {
                "length": self.dimensions_length,
                "width": self.dimensions_width,
                "depth": self.dimensions_depth
            }
        return {
            "name": self.name,
            "purchased_date": self.purchased_date,
            "price": self.price,
            "additional_data": {
                "expiration": self.expiration,
                "dimensions": dimensions
            }
        }

# Read YAML file and insert into the database
def load_orders_from_yaml(file_path):
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            orders_data = data["file_info"]["orders"]
            
            try:
                for category, items in orders_data.items():
                    for item_id, details in items.items():
                        additional_data = details.get("additional_data", {})
                        dimensions = additional_data.get("dimensions", {})
                        new_order = Order(
                            category=category,
                            name=details["name"],
                            purchased_date=details["purchased_date"],
                            price=details["price"],
                            expiration=additional_data.get("expiration"),
                            dimensions_length=dimensions.get("length") if dimensions else None,
                            dimensions_width=dimensions.get("width") if dimensions else None,
                            dimensions_depth=dimensions.get("depth") if dimensions else None
                        )
                        db.session.add(new_order)
                db.session.commit()  # Commit only after all insertions succeed

            except Exception as e:
                db.session.rollback()  # Rollback if any error occurs
                print(f"Transaction failed, rolled back: {e}")

            print("Sample data loaded successfully.")

    except Exception as e:
        print(f"Error loading file: {e}")  # File-related error handling


@app.before_request
def setup():
    db.create_all()
    if not Order.query.first():
        print("Database empty. Loading data from yaml fiel")
        load_orders_from_yaml("sample.yaml")
    else:
        print("Database already has data.")

#sample
@app.route("/")
def sample():
    return {"message": "assignment"}


#get method
@app.route("/orders", methods=["GET"])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])


#post
@app.route("/orders", methods=["POST"])
def add_new_order():
    new_orders = request.get_json()
    c = 0
    try:
        for order_data in new_orders:
            additional_data = order_data.get("additional_data", {})
            dimensions = additional_data.get("dimensions", {})
            try:
                new_order = Order(
                    category=order_data.get("category"),
                    name=order_data.get("name"),
                    purchased_date=order_data.get("purchased_date"),
                    price=order_data.get("price",None),
                    expiration=additional_data.get("expiration"),
                    dimensions_length=dimensions.get("length") if dimensions else None,
                    dimensions_width=dimensions.get("width") if dimensions else None,
                    dimensions_depth=dimensions.get("depth") if dimensions else None,
                )
                db.session.add(new_order)
                c += 1
            except KeyError as e:
                print(f"Key mismatch error: {e}")
                raise ValueError(f"Invalid input data: {e}")
        db.session.commit()
        return jsonify({"message": f"{c} orders added successfully."}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Transaction failed: {e}")
        return jsonify({"error": "Internal server error"}), 500

#filter
@app.route("/ordersFilter", methods=["GET"])
def get_filtered_orders():
    category = request.args.get("category")
    price = request.args.get("price")

    query = Order.query
    if category:
        query = query.filter_by(category=category)
    
    if price:
        query = query.filter_by(price=float(price))

    filtered_orders = query.all()
    print(filtered_orders)

    if filtered_orders:
        return jsonify([order.to_dict() for order in filtered_orders]), 200
    else:
        return jsonify({"message": "No orders found matching the criteria"}), 404

if __name__ == "__main__":
    app.run(port=5000, debug=True)




