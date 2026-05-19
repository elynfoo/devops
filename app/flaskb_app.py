import os
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config["DEBUG"] = True

comments = []

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Adding login support
app.secret_key = "password@123"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username


all_users = {
    "admin": User("admin", generate_password_hash("secret")),
    "bob": User("bob", generate_password_hash("less-secret")),
    "caroline": User("caroline", generate_password_hash("completely-secret")),
    "tester": User("tester", generate_password_hash("super-secret")),
}


@login_manager.user_loader
def load_user(user_id):
    return all_users.get(user_id)


# Mini Project: Part A - Define the Comment model BEFORE using it
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))


# Mini Project: Part A - Create the database tables
with app.app_context():
    db.create_all()


# Mini Project: Part A - simple website to post comments stored in a database
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template(
            "flaskwebsite/main_page.html", comments=Comment.query.all()
        )

    new_comment = Comment(content=request.form["contents"])
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for("index"))


# Mini Project: Part B
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("flaskwebsite/login_page.html", error=False)
    username = request.form["username"]
    if username not in all_users:
        return render_template("flaskwebsite/login_page.html", error=True)
    user = all_users[username]
    if not user.check_password(request.form["password"]):
        return render_template("flaskwebsite/login_page.html", error=True)
    login_user(user)
    return redirect(url_for('index'))


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
