from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import pickle
import numpy as np
import sqlite3

app = Flask(__name__)

# Configure JWT
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # Change this for security
jwt = JWTManager(app)

# Load trained model
with open("credit_fraud.pkl", "rb") as file:
    model = pickle.load(file)

# Dummy user database (Replace with real authentication if needed)
users = {"admin": "password123"}

# Initialize SQLite database
conn = sqlite3.connect("predictions.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS predictions 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   features TEXT, 
                   prediction TEXT)''')
conn.commit()

@app.route('/')
def home():
    return "Credit Card Fraud Detection API is running!"

# Login route to get authentication token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if users.get(username) == password:
        token = create_access_token(identity=username)
        return jsonify(access_token=token)

    return jsonify({"msg": "Invalid credentials"}), 401

# Prediction route (authentication required)
@app.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    data = request.get_json()
    features = data.get("features")

    if not features or len(features) != 30:
        return jsonify({"error": "Invalid input. Expecting 30 features."}), 400

    features_array = np.array(features).reshape(1, -1)
    prediction = model.predict(features_array)[0]
    result = "Fraudulent" if prediction == 1 else "Not Fraudulent"

    # Store in database
    cursor.execute("INSERT INTO predictions (features, prediction) VALUES (?, ?)", 
                   (str(features), result))
    conn.commit()

    return jsonify({"prediction": result})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)


