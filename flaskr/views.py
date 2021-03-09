from time import sleep
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
        query = (
            "SELECT * FROM features "
            + "ORDER BY ABS(coefficient) DESC"
        )
        rows = cursor.execute(query).fetchmany(100)
        if rows is None:
            return ("", 204)

        results = [
            {
                "feature": r["feature"],
                "coefficient": r["coefficient"],
                "frequency": r["frequency"]
            }
            for r in rows
        ]
        return jsonify(results)


@bp.route("get_confusion_matrix", methods=["POST"])
def get_confusion_matrix():
    if request.method == "POST":
        return json.load(open("classifier/results/confusion_matrix.json"))


@bp.route("/get_email", methods=["GET", "POST"])
def get_email():
    def fetch_emails(labels, offset, n, search_term=None):

        cursor = get_db().cursor()
        if search_term is None or search_term == "":
            if len(labels) == 1:
                label_filter = f"WHERE label in ({int(labels[0])}) "
            else:
                label_filter = " "


            query = (
                "SELECT * FROM messages "
                f"{label_filter}"
                f"LIMIT {n} OFFSET {offset};"
            )
            rows = cursor.execute(query).fetchmany(n)

        else:
            if len(labels) == 1:
                label_filter = f"AND label in ({int(labels[0])})"
            else:
                label_filter = " "


            search_query = (
                "SELECT"
                "    m.message_id,"
                "    m.label, "
                "    m.prob_spam, "
                "    highlight(fts_idx, 0, '<b>', '</b>') AS subject, "
                "    highlight(fts_idx, 1, '<b>', '</b>') AS body "
                "FROM fts_idx f JOIN messages m "
                "ON f.rowid = m.message_id "
                "WHERE fts_idx MATCH ? "
                f"{label_filter}"
                "ORDER BY bm25(fts_idx) "
                f"LIMIT {n} OFFSET {offset};"
            )
            rows = cursor.execute(search_query, (search_term,)).fetchmany(n)

        if rows is None:
            return None
        response = [
            {
                "id": r["message_id"],
                "label": r["label"],
                "subject": r["subject"],
                "body": "<br>".join(r["body"].split("<br>")[:6]),
                "prob_spam": int(r["prob_spam"] * 100),
            }
            for r in rows
        ]

        return response

    labels = []

    if request.method == "GET":

        if request.args.get("normal", "off") == "on":
            labels.append(0)
        if request.args.get("spam", "off") == "on":
            labels.append(1)
        if len(labels) == 0:
            return ("", 204)

        search_term = request.args.get("q", None)

        response = fetch_emails(labels, 0, 5, search_term=search_term)
        if response is None:
            return ("", 204)

        return render_template("search.html", response=response)

    elif request.method == "POST":
        if request.form.get("normal", "off") == "on":
            labels.append(0)
        if request.form.get("spam", "off") == "on":
            labels.append(1)

        search_term = request.form.get("q", "")
        offset = request.form.get("offset", 0)
        response = fetch_emails(
            labels, offset, 3, search_term=search_term
        )
        sleep(0.5)
        return render_template("search_scroll.html", response=response)


@bp.route("/item/<int:id>")
def item_page(id):
    cursor = get_db().cursor()
    response = cursor.execute(
        "SELECT subject, body FROM messages WHERE message_id=?", (id,)
    ).fetchone()
    return render_template("item.html", response=response)


@bp.route("/about")
def about_page():
    return render_template("about.html")


@bp.route("/classifier")
def classifier_page():
    return render_template("classifier.html")
