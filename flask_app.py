
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
# turn off in production
app.config["DEBUG"] = True

# Specifies that the following function defines the view for the “/” URL,
@app.route("/")
def index():
    return render_template("main_page.html")


# Flask decides if it’s GET or POST → Flask either shows the page or stores new data → browser reloads to show the updated page.
# Now Flask can handle both GET (viewing the page) and POST (submitting data).
@app.route("/contents", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=comments)
    comments.append(request.form["contents"])
    return redirect(url_for('index'))