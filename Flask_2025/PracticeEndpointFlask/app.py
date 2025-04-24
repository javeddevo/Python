from flask import Flask,request,jsonify
from db.db import db
app=Flask(__name__)

db=[{
    'id':1,
    'name':'John Doe',
    'author':'John',
    'description':'This is a test book',
},{
    'id':2,
    'name':'Jane Doe',
    'author':'Jane',
    'description':'This is another test book',
},{
    'id':3,
    'name':'Jim Doe',
    'author':'Jim',
    'description':'This is yet another test book',
  }]

@app.route('/',methods=['GET'])
def hello_world():
    return jsonify('<h1>Hello, World!<h1>')

@app.route('/books', methods=['GET'])
def get_books():
    return db

#path parameter
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    for book in db:
        if book["id"]==id:
            return book
    return {'error': 'Book not found'}, 404



#query parameter
@app.route('/books/search', methods=['GET'])
def search_books():
    author=request.args.get("author")
    if author:
        return [i for i in db if i["author"]==author]
    return {'error': 'Book not found'}, 404


#create a new book
@app.route('/books', methods=['POST'])
def add_book():
    book_details={
        "id":len(db)+1,
        "name":request.json["name"],
        "author":request.json["author"],
        "description":request.json["description"]
    }
    db.append(book_details)
    return book_details, 201

#update a book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    for book in db:
        if book["id"]==id:
            book["name"]=request.json["name"]
            book["author"]=request.json["author"]
            book["description"]=request.json["description"]
            return book
    return {'error': 'Book not found'}, 404

# delete a book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    for index,book in enumerate(db):
        if book["id"]==id:
            db.pop(index)
            return jsonify({'message': f'Book with id:{id} is deleted successfully'}), 200

    return jsonify({'error': 'Book not found'}), 404
app.run(debug=True)