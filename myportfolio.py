from flask import Flask, render_template, redirect, url_for 
 
app = Flask(__name__)
app.config["DEBUG"] = True

# -----------------------------
# Portfolio routes
@app.route("/")
def home():
    return redirect(url_for("portfolio"))

@app.route("/portfolio")
def portfolio():
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
