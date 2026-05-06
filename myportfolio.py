import os
from flask import Flask, render_template, redirect, url_for, request, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# -----------------------------
# Flask App
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"   # required for sessions

# Configure SQLite with SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, "portfolio.db")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{database_path}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Add user in bash/flask
#   export FLASK_APP=myportfolio:app
#   flask shell
#   from myportfolio import db
#   from myportfolio import User
#   User.query.all()
# SQLite Shell
#   db.create_all()
#   sqlite3 /home/elynfoo/portfolio.db
#   .tables
#   .schema user
#   SELECT * FROM user;

# -----------------------------
# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -----------------------------
# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------
# Initialize database tables
with app.app_context():
    db.create_all()

# -----------------------------
# Role-based decorator
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# -----------------------------
# Login routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            # Failed login → show login page with error and link to register
            return render_template("flaskwebsite/login_page.html", error=True)
    # GET request → show login form with no error
    return render_template("flaskwebsite/login_page.html", error=False)
# -----------------------------
# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return render_template("flaskwebsite/register_page.html", error="Username already taken")

        # Create new user
        new_user = User(username=username, role="user")
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # Auto-login after registration
        login_user(new_user)
        return redirect(url_for("dashboard"))

    return render_template("flaskwebsite/register_page.html", error=None)

# -----------------------------
# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/admin")
@login_required
@role_required("admin")
def admin():
    return "Welcome Admin!"



# -----------------------------
# routes
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("dashboard")) #public dashboard

# -----------------------------
# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        # Logged in → show private dashboard
        return render_template("portfolio/dashboard.html", user=current_user)
    else:
        # Not logged in → show public dashboard
        return render_template("portfolio/dashboard.html")

@app.route("/public-dashboard")
def public_dashboard():
    return render_template("portfolio/dashboard.html")

@app.route("/python")
def python():
    return render_template("portfolio/python.html")

@app.route("/linux")
def linux():
    return render_template("portfolio/linux.html")

@app.route("/devops")
def devops():
    return render_template("portfolio/devops.html")

@app.route("/others")
def others():
    return render_template("portfolio/others.html")
