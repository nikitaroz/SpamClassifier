

from flask import jsonify, render_template, request, redirect, json
from flaskr.db import get_db
from flask import Blueprint
bp = Blueprint("main", __name__)

# TODO: remove
from numpy.random import randint

@bp.route("/")
def main():
    return render_template("main.html")

@bp.route("/get_top_features", methods=["POST"])
def get_top_features():
    if request.method == "POST":
        cursor = get_db().cursor()
        query = f"SELECT feature, coefficient FROM features " + \
            f"ORDER BY ABS(coefficient) DESC"
        rows = cursor.execute(query).fetchmany(100)
        if rows is None:
            return ("", 204)
        # TODO: unstem
        # TODO: frequency
        results = [{
            "feature": r["feature"],
            "coefficient": r["coefficient"],
            "frequency": randint(low=1, high=1000),
            "words": "this is a test",
            } for r in rows]
        return jsonify(results)

@bp.route("get_confusion_matrix", methods=["POST"])
def get_confusion_matrix():
    if request.method == "POST":
        return json.load(open("classifier/results/confusion_matrix.json"))
    

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
        query = f"SELECT message_id, label, subject, body, prob_spam FROM messages WHERE " + \
            f"(prob_spam BETWEEN ? AND ?) AND " + \
            f"(label IN ({', '.join(len(labels)*['?'])})) " + \
            f"ORDER BY RANDOM()"
        rows = cursor.execute(
            query,
            (prob_min, prob_max, *labels)
        ).fetchmany(1)
        if rows is None:
            return ("", 204)
        results = [{
            "id": r["message_id"], 
            "label": r["label"],
            "subject": r["subject"], 
            "body": r["body"],
            "prob_spam": r["prob_spam"]
            } for r in rows]
        return jsonify(results)


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
        else:
            return redirect("/")

@bp.route("/item", methods=["GET"])
def item_page():
    if request.method == "GET":
        try:
            id = request.args.get("id", "")
        except ValueError:
            return redirect("/")
        cursor = get_db().cursor()
        result = cursor.execute(
            "SELECT subject, body FROM messages WHERE message_id=?", (id,)
        ).fetchone()
        subject, body = result
        return render_template("item.html", subject=subject, body=body)

@bp.route("/about")
def about_page():
    return render_template("about.html")


@bp.route("/classifier")
def classifier_page():
    return render_template("classifier.html")
