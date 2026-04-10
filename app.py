from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# 🔐 Config
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🔐 Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'   # ✅ FIX: redirect instead of 401


# 👤 User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))


# 🔄 Load User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 🏠 Home (Protected)
@app.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)


# 🔐 Login Page (GET)
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


# 🔐 Login Logic (POST)
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    # ✅ Check user + password
    if user and user.password == password:
        login_user(user)
        return redirect(url_for('home'))
    else:
        return "Invalid email or password"


# 📝 Signup Page (GET)
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


# 📝 Signup Logic (POST)
@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # ❌ Prevent duplicate users
    user = User.query.filter_by(email=email).first()
    if user:
        return "Email already exists"

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)  # auto login after signup
    return redirect(url_for('home'))


# 🚪 Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# 🔧 Create DB automatically
with app.app_context():
    db.create_all()


# ▶️ Run App
if __name__ == "__main__":
    app.run(debug=True)