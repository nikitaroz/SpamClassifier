import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from matplotlib.colors import to_hex
import sqlite3
import seaborn as sns
import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex

import matplotlib as mpl 
import matplotlib.cm as cm

norm = mpl.colors.Normalize(vmin=-20, vmax=20)
cmap = cm.get_cmap("coolwarm")

m = cm.ScalarMappable(norm=norm, cmap=cmap)


def custom_tokenizer(nlp):
    infixes = nlp.Defaults.infixes + tuple([r"\b[\[\(]\b"]) 
    infix_re = compile_infix_regex(infixes)
    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)
    return Tokenizer(
        nlp.vocab,
        prefix_search=prefix_re.search,
        suffix_search=suffix_re.search,
        infix_finditer=infix_re.finditer,
        token_match=None
    )

nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner", "textcat"])
nlp.tokenizer = custom_tokenizer(nlp)

from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

@app.route('/')
def main():
    #db_connector = sqlite3.connect("db/spam.db")
    #cursor = db_connector.cursor()
    #email_text = cursor.execute("SELECT text FROM messages where ID=1").fetchall()[0][0]
    return render_template("main.jinja")#, email_text=email_text)

@app.route("/get_spam")
def get_spam():
    spam_slider_val = request.args.get("spamSliderVal", 50)
#    print(jsonify(spam = spamsss))
    conn = sqlite3.connect("db/spam.db")
    cursor = conn.cursor()

    subject, body = cursor.execute(f"SELECT subject, body FROM messages where message_id={spam_slider_val}").fetchone()
    #subject = subject.replace("\n", "<br>")
    cmap = sns.color_palette("viridis", as_cmap=True)
    
    tokens = []
    conn = sqlite3.connect("db/spam.db")
    cursor = conn.cursor()
    # TODO: don't query if common word, etc...
    # TODO: grouped query possible here???
    # TODO: this should use the classmethod from Message
    for token in nlp(body):
        result = cursor.execute("SELECT coefficient FROM features WHERE feature == ?", (token.text,)).fetchone()
        if result is not None:
            #print(result)
            color = to_hex(m.to_rgba(result[0]))
            #print(m.to_rgba(result))

            tokens.append(f"<mark style='background-color:{color};'>" + token.text + "</mark>")
        else:
            tokens.append(token.text)
        if token.whitespace_:
            tokens.append(token.whitespace_)
    tokens = "".join(tokens)
    
    
    body = body.replace("\n", "<br>")
    tokens = tokens.replace("\n", "<br>")
    return jsonify(subject=subject, body=" ", tokens=tokens)



@app.route("/about")
def about_page():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)