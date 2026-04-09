from flask import Flask, request, jsonify, render_template
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)

# CORS frontend (HTML) aur backend (Python) ko connect karne deta hai
CORS(app)

# Security Key (Token banane ke liye)
app.config['SECRET_KEY'] = 'super_secret_internship_key'

# Mock Database (Abhi ke liye list use kar rahe hain)
users = []
@app.route('/')
def home():
    return render_template('login.html')

# ==========================================
# SIGN UP API (Naya Account Banane Ke Liye)
# ==========================================
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    password = data.get('password')

    # Check agar user pehle se exist karta hai
    if any(user['email'] == email for user in users):
        return jsonify({"message": "User already exists with this email!"}), 400

    # Password encrypt karna
    hashed_password = generate_password_hash(password)
    
    # User save karna
    new_user = {
        "id": len(users) + 1,
        "fullname": fullname,
        "email": email,
        "password": hashed_password
    }
    users.append(new_user)
    print("Database Updated -> Users:", users)

    return jsonify({"message": "Account created successfully!"}), 201

# ==========================================
# LOGIN API (Sign In Karne Ke Liye)
# ==========================================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # User dhundna
    user = next((u for u in users if u['email'] == email), None)
    
    # Agar user nahi mila ya password galat hai
    if not user or not check_password_hash(user['password'], password):
        return jsonify({"message": "Invalid email or password"}), 400

    # Agar password sahi hai, toh 1 ghante ke liye Token generate karo
    token = jwt.encode({
        'userId': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "message": f"Welcome back, {user['fullname']}!",
        "token": token,
        "user": {"fullname": user['fullname'], "email": user['email']}
    }), 200

# ==========================================
# Server Run Command
# ==========================================
if __name__ == '__main__':
    print("🚀 Flask Backend is running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
