from flask import Flask, render_template


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config["DEBUG"] = True


@app.route("/")
def home():
    return render_template("about_me.html")
