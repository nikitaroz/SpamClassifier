import os
import sys

module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)

from common.database_connector import DatabaseConnector
from flask import Flask, jsonify, render_template, request

db = DatabaseConnector("../db/spam.db", None, None)
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/get_email", methods=["POST"])
def get_email():
    if request.method == "POST":
        labels = []
        if request.args.get("hasNormal", True): labels.append(0)
        if request.args.get("hasSpam", True): labels.append(1)
        prob_min = request.args.get("sliderMin", 0) / 100
        prob_max = request.args.get("sliderMax", 1) / 100
    
        if len(labels) == 0:
            return ("", 204)
        query = f"SELECT subject, body FROM messages WHERE  " + \
            f"(prob_spam BETWEEN ? AND ?) AND " + \
            f"(label IN ({', '.join(len(labels)*['?'])})) " + \
            f"ORDER BY RANDOM()"
        result = db.cursor.execute(
            query,
            (prob_min, prob_max, *labels)
        ).fetchone()
        if result is None:
            return ("", 204)
        subject, body = result
        return jsonify(subject=subject, body=body)


# https://stackoverflow.com/questions/52904116/flask-use-the-same-view-to-render-a-search-form-and-then-search-results/52905054
@app.route("/search", methods=["GET"])
def search():
    # TODO: validate input
    if request.method == "GET":
        search_term = request.args.get("q", "")
        if search_term != "":
            results = db.cursor.execute(
                "SELECT highlight(fts_idx, 0, '<b>', '</b>'), " + \
                "highlight(fts_idx, 1, '<b>', '</b>') " + \
                "FROM fts_idx WHERE fts_idx MATCH ? ORDER BY rank;",
                (search_term,),
            ).fetchmany(5)
            return render_template("search.html", results=results)

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/classifier")
def classifier_page():
    return render_template("classifier.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
