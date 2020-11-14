import os
import sys

module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)

from common.database_connector import DatabaseConnector
from flask import Flask, jsonify, render_template, request
from numpy.random import randint

db = DatabaseConnector("db/spam.db")
app = Flask(__name__)


@app.route("/")
def main():
    return render_template("main.jinja")


@app.route("/get_email")
def get_email():

    value = randint(0, 10)
    subject, body = db.cursor.execute(
        "SELECT subject, body FROM messages where message_id=?", (value,)
    ).fetchone()

    return jsonify(subject=subject, body=body)


# https://stackoverflow.com/questions/52904116/flask-use-the-same-view-to-render-a-search-form-and-then-search-results/52905054
@app.route("/search", methods=["GET", "POST"])
def search():
    # TODO: validate input
    if request.method == "GET":
        search_term = request.args.get("q", "")
        results = db.cursor.execute(
            "SELECT subject, body FROM fts_idx WHERE fts_idx MATCH ? ORDER BY rank",
            (search_term,),
        ).fetchmany(5)
    return render_template("search.jinja", results=results)


@app.route("/about")
def about_page():
    return render_template("about.jinja")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
