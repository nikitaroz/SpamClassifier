import re
from os.path import exists

import ftfy
import mailparser
import nltk
from bs4 import BeautifulSoup
from mailparser.mailparser import MailParser
from nltk.corpus import stopwords, words
from nltk.stem import SnowballStemmer
from nltk.tokenize import TweetTokenizer

try:
    nltk.data.find("corpora/words")
except LookupError:
    nltk.download("words")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

TOKENIZER = TweetTokenizer()

STEMMER = SnowballStemmer("english")
WORDS = set(STEMMER.stem(w) for w in words.words())
STOPWORDS = set(STEMMER.stem(w) for w in stopwords.words("english"))


class Message:
    def __init__(self, message):

        if isinstance(message, str) and exists(message):
            self._parser = mailparser.parse_from_file(message)
        elif isinstance(message, MailParser):
            self._parser = message
        elif isinstance(message, str):
            self._parser = mailparser.parse_from_string(message)
        else:
            raise ValueError("Could not parse message.")

        self._body = ftfy.fix_text(self._parser.body)
        self._subject = ftfy.fix_text(self._parser.headers.get("Subject", ""))
        self._normalized_text = self._normalize_text(self.subject + "\n\n" +
                                                     self.body)
        self._tokenizer = TOKENIZER
        self._stemmer = STEMMER
        self._words = WORDS
        self._stopwords = STOPWORDS

    @property
    def tokenizer(self):
        return self._tokenizer

    @property
    def stemmer(self):
        return self._stemmer

    @property
    def body(self):
        return self._body

    @property
    def subject(self):
        return self._subject

    def text_features(self):
        features = {
            "cap_max": 0,
            "cap_pct": 0,
            "num_links": 0,
            "has_html": False,
            "nonascii_pct": 0,
        }

        if re.search(r"<\/?[a-zA-Z]*>", self.body) is not None:
            features["has_html"] = True

        soup = BeautifulSoup(self.body, "html.parser")

        features["num_links"] = len(soup.find_all("a", href=True))
        char_len = len(self._normalized_text)
        if char_len > 0:
            num_nonascii = 0
            for char in self._normalized_text:
                if ord(char) > 128:
                    num_nonascii += 1
            features["nonascii_pct"] = num_nonascii / char_len

        # finds continuous lines of capital letters
        caps = re.finditer(r"[A-Z]{2,}.*?(?=(?:\W?[A-Z]?[a-z]|$))",
                           self._normalized_text)
        cap_lengths = []
        for match in caps:
            cap_lengths.append(len(match.group()))
        if len(cap_lengths) > 0:
            features["cap_max"] = max(cap_lengths)
            features["cap_pct"] = sum(cap_lengths) / char_len

        return features

    def _normalize_text(self, text):
        if re.search(r"<\/?[a-zA-Z]*>", text) is not None:
            soup = BeautifulSoup(text, "html.parser")
            normalized_text = soup.get_text(separator=" ")
        else:
            normalized_text = text

        normalized_text = re.sub(r"(?:\s*\n\s*){2,}", r"\n\n", normalized_text)

        return normalized_text

    def tokens(self):
        tokens = self.tokenizer.tokenize(self._normalized_text)
        stems = [self.stemmer.stem(t).lower() for t in tokens]
        filtered_tokens = [
            t for t in stems if t in self._words and t not in self._stopwords
        ]
        return " ".join(filtered_tokens)

    def subject_html(self, db_connector=None):
        subject = self._normalize_text(self.subject)
        return self._get_html(subject, db_connector)

    def body_html(self, db_connector=None):
        body = self._normalize_text(self.body)
        return self._get_html(body, db_connector)

    def _get_html(self, text, db_connector):
        tokens = []
        cursor = 0
        text_len = len(text)
        for token in self.tokenizer.tokenize(text):
            size = len(token)
            while True:
                if text[cursor:cursor + size] == token:
                    stem = self.stemmer.stem(token)
                    if db_connector is not None:
                        result = db_connector.cursor.execute(
                            "SELECT coefficient FROM features WHERE feature == ?",
                            (stem, ),
                        ).fetchone()
                        if result is not None:
                            coef = result[0]
                            tokens.append(f"<mark data-value='{coef:.5}'>" +
                                          token + "</mark>")
                        else:
                            tokens.append(token)
                    else:
                        tokens.append(token)
                    cursor += size
                    break
                else:
                    if text_len == cursor:
                        break
                    elif text[cursor] == "\n":
                        tokens.append("<br>")
                    else:
                        tokens.append(text[cursor])
                    cursor += 1

        tokens = "".join(tokens)
        return tokens
