import sys

from flask import Flask, request
from flask.templating import render_template

from dbhelper import DBHelper


app = Flask(__name__)
db = DBHelper()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin", methods=["POST", "GET"])
def admin_page():
    if request.method == "POST":
        from_time = request.form["from_time"]
        to_time = request.form["to_time"]

        if from_time == "" or to_time == "":
            return render_template("admin.html")
        
        # prepare time
        from_time = from_time.replace('T', ' ')
        from_time += ':00'
        to_time = to_time.replace('T', ' ')
        to_time += ':00'

        users = db.search_users(from_time, to_time)
        return render_template('admin.html', users=list(enumerate(users)), table=True)

    return render_template("admin.html", table=False)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print(f"Usage: ./{sys.argv[0]} <port>")
        exit(0)
    port = int(sys.argv[1])
    app.run(host="127.0.0.1", port=port)