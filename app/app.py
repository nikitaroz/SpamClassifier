import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import sqlite3

from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

@app.route('/')
def main():
    db_connector = sqlite3.connect("db/spam.db")
    cursor = db_connector.cursor()
    email_text = cursor.execute("SELECT text FROM messages where ID=1").fetchall()[0][0]
    return render_template("main.jinja", email_text=email_text)

@app.route("/get_spam")
def get_spam():
    spam_slider_val = request.args.get("spamSliderVal", 50)
#    print(jsonify(spam = spamsss))
    conn = sqlite3.connect("db/spam.db")
    cursor = conn.cursor()
    email_text = cursor.execute(f"SELECT text FROM messages where ID={spam_slider_val}").fetchall()[0][0]

    return jsonify(email_text = email_text.replace("\n", "<br>"))



@app.route("/about")
def about_page():
    return render_template("about.html")