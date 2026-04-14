from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.config["DEBUG"] = True

## user authentication and permissions
from flask import request, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "supersecret"   # required for sessions

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Demo users
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        if username in users:
            login_user(users[username])
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Hello {current_user.username}, role: {current_user.role}"

@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        abort(403)   # Forbidden
    return "Welcome Admin!"


#----------------------------------------------------------------------------
#redirect
@app.route("/")
def home():
    return redirect(url_for("portfolio"))

#portfolio page - show case progress dashboard
@app.route("/portfolio")
def portfolio():
    return render_template("portfolio/dashboard.html")

#portfolio page - show case progress dashboard
@app.route("/python")
def python():
    return render_template("portfolio/python.html")
#portfolio page - show case progress dashboard
@app.route("/linux")
def linux():
    return render_template("portfolio/linux.html")
#portfolio page - show case progress dashboard
@app.route("/devops")
def devops():
    return render_template("portfolio/devops.html")
#portfolio page - show case progress dashboard
@app.route("/others")
def others():
    return render_template("portfolio/others.html")
