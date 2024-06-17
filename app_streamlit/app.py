from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data (normally this would be in a database)
data = {
    "users": [
        {"id": 1, "name": "John Doe", "age": 30, "email": "john@example.com"},
        {"id": 2, "name": "Jane Doe", "age": 25, "email": "jane@example.com"}
    ]
}

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(data["users"])

@app.route('/api/users', methods=['POST'])
def add_user():
    new_user = request.json
    data["users"].append(new_user)
    return jsonify(new_user), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    updated_user = request.json
    for user in data["users"]:
        if user["id"] == user_id:
            user.update(updated_user)
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global data
    data["users"] = [user for user in data["users"] if user["id"] != user_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ensure this port matches the Streamlit configuration
