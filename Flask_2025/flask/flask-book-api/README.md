# Flask Book API

This is a simple Flask application that provides a RESTful API for managing a collection of books. 

## Project Structure

- `src/app.py`: Entry point of the application.
- `src/controllers/book_controller.py`: Contains the `BookController` class for handling book-related requests.
- `src/services/book_service.py`: Contains the `BookService` class for business logic related to books.
- `src/models/book.py`: Defines the `Book` model structure.
- `src/routes/book_routes.py`: Sets up the routes for book-related endpoints.
- `src/database/db.py`: Manages database connections and operations.
- `requirements.txt`: Lists the dependencies required for the project.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd flask-book-api
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/app.py
```

The API will be available at `http://localhost:5000`. 

## Endpoints

- `GET /books`: Retrieve a list of all books.
- `GET /books/<id>`: Retrieve a specific book by ID.
- `POST /books`: Add a new book.
- `PUT /books/<id>`: Update an existing book.
- `DELETE /books/<id>`: Delete a book by ID.

## License

This project is licensed under the MIT License.