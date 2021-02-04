import subprocess
from flask import Flask
from flask.templating import render_template
import subprocess


app = Flask(__name__)

END_TIME = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin_page():
    return "In Progress..."

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)