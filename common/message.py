import re

import ftfy
#import mailparser
import numpy as np
from bs4 import BeautifulSoup
from matplotlib.cm import ScalarMappable, get_cmap
from matplotlib.colors import Normalize, to_hex
from nltk.corpus import stopwords, words
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer


STEMMER = PorterStemmer()

WORDS = set(STEMMER.stem(w) for w in words.words())
STOPWORDS = set(STEMMER.stem(w) for w in stopwords.words("english"))


class Message:
    def __init__(self, parser: str):
        
        self.parser = parser
        self._body = ftfy.fix_text(self.parser.body)
        self._subject = ftfy.fix_text(parser.headers.get("Subject", ""))

        self._tokenizer = TweetTokenizer()
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
            "has_html": False,
            "nonascii_pct": 0,
        }

        text = self.subject + "\n\n" + self.body
        if re.search(r"<\/?[a-zA-Z]*>", text) is not None:
            features["has_html"] = True

        normalized_text = self._normalize_text(text)

        char_len = len(normalized_text)
        if char_len > 0:
            num_nonascii = 0
            for char in normalized_text:
                if ord(char) > 128:
                    num_nonascii += 1
            features["nonascii_pct"] = num_nonascii / char_len

        caps = re.finditer(r"[A-Z]{2,}.*?(?=(?:\W?[A-Z]?[a-z]|$))", normalized_text)
        cap_lengths = []
        for match in caps:
            cap_lengths.append(len(match.group()))
        if len(cap_lengths) > 0:
            cap_lengths = np.array(cap_lengths)
            features["cap_max"] = cap_lengths.max()
            features["cap_pct"] = cap_lengths.sum() / len(normalized_text)

        return features

    # TODO: apparently this does not actually remove html
    def _normalize_text(self, text):
        if re.search(r"<\/?[a-zA-Z]*>", text) is not None:
            soup = BeautifulSoup(text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                if a_tag.string is None:
                    a_tag.string = a_tag.get("href")
                else:
                    a_tag.string = a_tag.string + " " + a_tag.get("href")
            normalized_text = soup.get_text(separator=" ")
        else:
            normalized_text = text

        normalized_text = re.sub(r"(?:\s*\n\s*){2,}", r"\n\n", normalized_text)

        return normalized_text

    def tokens(self):
        text = self.subject + "\n\n" + self.body
        normalized_text = self._normalize_text(text)

        tokens = self.tokenizer.tokenize(normalized_text)
        stems = [self.stemmer.stem(t).lower() for t in tokens]
        filtered_tokens = [
            t for t in stems if t in self._words and t not in self._stopwords
        ]
        return " ".join(filtered_tokens)

    def subject_html(self, db_connector=None, scalar_map=None):
        subject = self._normalize_text(self.subject)
        return self._get_html(subject, db_connector, scalar_map)

    def body_html(self, db_connector=None, scalar_map=None):
        body = self._normalize_text(self.body)
        return self._get_html(body, db_connector, scalar_map)

    def _get_html(self, text, db_connector, scalar_map):
        tokens = []
        if scalar_map is None:
            norm = Normalize(vmin=-20, vmax=20)
            cmap = get_cmap("coolwarm")
            scalar_map = ScalarMappable(norm=norm, cmap=cmap)
        cursor = 0
        text_len = len(text)
        for token in self.tokenizer.tokenize(text):
            size = len(token)
            while True:
                if text[cursor : cursor + size] == token:
                    stem = self.stemmer.stem(token)
                    if db_connector is not None:
                        coef = db_connector.cursor.execute(
                            "SELECT coefficient FROM features WHERE feature == ?",
                            (stem,),
                        ).fetchone()
                        if coef is not None:
                            color = to_hex(scalar_map.to_rgba(coef[0]))
                            tokens.append(
                                f"<mark style='background-color:{color};'>"
                                + token
                                + "</mark>"
                            )
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
