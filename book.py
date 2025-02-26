from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

MONGODB_URI = "mongodb+srv://User:<db_password>@cluster0.0eyjo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "book_database"

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
books_collection = db["books"]

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Create (POST) 
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()

    if not data.get("title") or not data.get("author") or not data.get("image_url"):
        return jsonify({"error": "Missing required fields"}), 400

    new_book = {
        "title": data["title"],
        "author": data["author"],
        "image_url": data["image_url"]
    }
    result = books_collection.insert_one(new_book)
    new_book["_id"] = str(result.inserted_id) 

    return jsonify(new_book), 201

# Read (GET) 
@app.route('/books', methods=['GET'])
def get_all_books():
    books = list(books_collection.find({}))
    for book in books:
        book["_id"] = str(book["_id"])  
    return jsonify({"books": books})

# Read (GET) 
@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:

        book = books_collection.find_one({"_id": ObjectId(book_id)})
        if book:
            book["_id"] = str(book["_id"]) 
            return jsonify(book)
        return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid ID format"}), 400

# Update (PUT) 
@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        
        data = request.get_json()
        if "_id" in data:
            del data["_id"]
        update_data = {k: v for k, v in data.items() if v}

        result = books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": update_data})

        if result.matched_count == 0:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({"message": "Book updated successfully"})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Invalid ID format"}), 400

# Delete (DELETE) 
@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        result = books_collection.delete_one({"_id": ObjectId(book_id)})

        if result.deleted_count == 0:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({"message": "Book deleted successfully"})
    except Exception as e:
        return jsonify({"error": "Invalid ID format"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)