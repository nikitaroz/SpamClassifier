

from flask import jsonify, render_template, request
from flaskr.db import get_db
from flask import Blueprint
bp = Blueprint("main", __name__)

@bp.route("/")
def main():
    return render_template("main.html")


@bp.route("/get_email", methods=["POST"])
def get_email():
    if request.method == "POST":
        cursor = get_db().cursor()

        labels = []
        if "hasNormal" in request.form: labels.append(0)
        if "hasSpam" in request.form: labels.append(1)
        prob_min = float(request.form.get("sliderMin", 0)) / 100
        prob_max = float(request.form.get("sliderMax", 1)) / 100
        if len(labels) == 0:
            return ("", 204)
        query = f"SELECT subject, body FROM messages WHERE " + \
            f"(prob_spam BETWEEN ? AND ?) AND " + \
            f"(label IN ({', '.join(len(labels)*['?'])})) " + \
            f"ORDER BY RANDOM()"
        print(query)
        result = cursor.execute(
            query,
            (prob_min, prob_max, *labels)
        ).fetchone()
        print(prob_min, prob_max, *labels)
        print(result)
        if result is None:
            return ("", 204)
        subject, body = result
        return jsonify(subject=subject, body=body)


@bp.route("/search", methods=["GET"])
def search():
    # TODO: validate input
    if request.method == "GET":
        cursor = get_db().cursor()
        search_term = request.args.get("q", "")
        if search_term != "":
            results = cursor.execute(
                "SELECT highlight(fts_idx, 0, '<b>', '</b>'), " + \
                "highlight(fts_idx, 1, '<b>', '</b>') " + \
                "FROM fts_idx WHERE fts_idx MATCH ? ORDER BY rank;",
                (search_term,),
            ).fetchmany(5)
            return render_template("search.html", results=results)


@bp.route("/about")
def about_page():
    return render_template("about.html")


@bp.route("/classifier")
def classifier_page():
    return render_template("classifier.html")
