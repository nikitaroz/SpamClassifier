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
<<<<<<< HEAD
#    db_connector = sqlite3.connect("db/spam.db")
#    cursor = db_connector.cursor()
#    email_text = cursor.execute("SELECT text FROM messages where ID=1").fetchall()[0][0]
    return render_template("main.jinja", subject="", body="")
=======
    #db_connector = sqlite3.connect("db/spam.db")
    #cursor = db_connector.cursor()
    #email_text = cursor.execute("SELECT text FROM messages where ID=1").fetchall()[0][0]
    return render_template("main.jinja")#, email_text=email_text)
>>>>>>> 8f18afe934b972cbbebf5d6719840330bbb3593b

@app.route("/get_spam")
def get_spam():
    spam_slider_val = request.args.get("spamSliderVal", 50)
#    print(jsonify(spam = spamsss))
    conn = sqlite3.connect("db/spam.db")
    cursor = conn.cursor()

    subject, body = cursor.execute(f"SELECT subject, body FROM messages where message_id={spam_slider_val}").fetchone()
    #subject = subject.replace("\n", "<br>")
    body = body.replace("\n", "<br>")
    return jsonify(subject=subject, body=body)



@app.route("/about")
def about_page():
    return render_template("about.html")