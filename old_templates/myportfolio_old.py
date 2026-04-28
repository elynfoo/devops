from flask import Flask, render_template, redirect, url_for, request, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"   # required for sessions
 
# Demo users with DB 
db = SQLAlchemy()
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
# -----------------------------
# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


# Static # Demo users (replace with DB later)
users = {
    "admin": User("1", "admin", "admin"),
    "guest": User("2", "guest", "user")
}

@login_manager.user_loader
def load_user(user_id):
    for u in users.values():
        if u.id == user_id:
            return u
    return None

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
# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")

        # Check if user exists
        if username not in users:
            return render_template("flaskwebsite/login_page.html", error=True)

        user = users[username]

        # For now, demo users don’t have password checks
        # You can add user.check_password(password) later
        login_user(user)
        return redirect(url_for("dashboard"))

    # GET request → show login form with no error
    return render_template("flaskwebsite/login_page.html", error=False)


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
# Portfolio routes
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("public_dashboard"))

#@app.route("/")
#def home():
#    if current_user.is_authenticated:
#        return redirect(url_for("dashboard"))
#    return redirect(url_for("public_dashboard"))

@app.route("/public-dashboard")
def public_dashboard():
    return render_template("portfolio/dashboard.html")

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        # Logged in → show private dashboard
        return render_template("portfolio/dashboard.html", user=current_user)
    else:
        # Not logged in → show public dashboard
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
