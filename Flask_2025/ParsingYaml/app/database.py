import yaml
import logging
from . import db
from .models import Order

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_yaml_data():
    try:
        with open('sample.yaml', 'r') as file:
            logger.info("Loading sample.yaml")
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error("sample.yaml file not found")
        raise Exception("sample.yaml file not found")
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {str(e)}")
        raise Exception(f"Error parsing YAML file: {str(e)}")

def init_db(app):
    with app.app_context():
        logger.info("Creating database tables")
        db.create_all()
        data = load_yaml_data()
        
        # Clear existing data
        logger.info("Clearing existing orders")
        Order.query.delete()
        
        orders = data.get('file_info', {}).get('orders', {})
        
        # Process edibles
        for _, item in orders.get('edibles', {}).items():
            order = Order(
                name=item['name'],
                purchased_date=item['purchased_date'],
                price=item['price'],
                category='edibles',
                expiration=item['additional_data']['expiration'],
                dimensions_length=None,
                dimensions_width=None,
                dimensions_depth=None
            )
            db.session.add(order)
            logger.info(f"Added edible order: {item['name']}")
        
        # Process others (if any)
        for _, item in orders.get('others', {}).items():
            dimensions = item['additional_data'].get('dimensions', {})
            order = Order(
                name=item['name'],
                purchased_date=item['purchased_date'],
                price=item['price'],
                category='others',
                expiration=item['additional_data'].get('expiration'),
                dimensions_length=dimensions.get('length') if dimensions else None,
                dimensions_width=dimensions.get('width') if dimensions else None,
                dimensions_depth=dimensions.get('depth') if dimensions else None
            )
            db.session.add(order)
            logger.info(f"Added other order: {item['name']}")
        
        db.session.commit()
        logger.info("Database initialization completed")