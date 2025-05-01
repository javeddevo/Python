from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To avoid warning

# Secret key (I'll explain why below)
app.config['SECRET_KEY'] = "random_secret_string"

db = SQLAlchemy(app)

# Model
class Student(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200)) 
    pin = db.Column(db.String(10))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'addr': self.addr,
            'pin': self.pin
        }

# API to get all students
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

# API to add a new student
# @app.route('/students', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     new_student = Student(
#         name=data['name'],
#         city=data['city'],
#         addr=data['addr'],
#         pin=data.get('pin')  # optional
#     )
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({'message': 'Student added successfully'}), 201
@app.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json()

        # Check required fields manually
        required_fields = ['name', 'city', 'addr']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        new_student = Student(
            name=data['name'],
            city=data['city'],
            addr=data['addr'],
            pin=data.get('pin')  # optional
        )
        db.session.add(new_student)
        db.session.commit()

        return jsonify({'message': 'Student added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if not exist
    app.run(debug=True)
