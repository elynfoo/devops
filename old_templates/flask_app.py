
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []

#configure SQLite in flask_app.py
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/elynfoo/comments.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))


#redirect
@app.route("/")
def home():
    return redirect(url_for("index"))

@app.route("/flaskwebsite", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #return render_template("main_page.html", comments=comments)
        return render_template("flaskwebsite/main_page.html", comments=Comment.query.all())

    new_comment = Comment(content=request.form["contents"])
    # comments.append(request.form["contents"])
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for("index"))

