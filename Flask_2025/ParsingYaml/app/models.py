from . import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    purchased_date = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
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