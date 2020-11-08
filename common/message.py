import re
from urllib.parse import urlparse

import ftfy
import mailparser
import numpy as np

# import pandas as pd
import spacy
#import unidecode

from bs4 import BeautifulSoup

# from sklearn.base import BaseEstimator, TransformerMixin
# from sklearn.compose import ColumnTransformer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import StandardScaler

nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner", "textcat"])


class Message:
    def __init__(
        self, mailparser_obj: mailparser.MailParser, label, special_chars="!?*$%#*{[("
    ):
        self.mailparser_obj = mailparser_obj
        self.label = label
        message_body = mailparser_obj.body
        if re.match(r"<\/?[a-zA-Z]*>", message_body) is not None:
        #    self.body_has_html = True
            soup = BeautifulSoup(message_body, "html.parser")
        #    for link in soup.find_all("a", href=True):
        #        for token in urlparse(link["href"]).netloc.split("."):
        #            body_urls.append(token)

            message_body = soup.get_text(separator=" ")

        self.text = message_body
        self.subject = self.mailparser_obj.headers.get("Subject", "")
        # TODO: do not make these class attributes
        self.body_cap_max = 0
        self.body_cap_pct = 0
        self.body_tokens = ""
        # self.subject_tokens = ""
        self.body_nonascii_pct = 0
        self.body_has_html = False
        # self.body_urls = ""
        # self.body_emails = ""
        self.sender = ""
        # self.body_char_len = 0
        self.special_chars = special_chars
        self.body_special_char_pct = dict(
            zip(self.special_chars, len(self.special_chars) * [0])
        )

    def extract_features(self):
        self._extract_body_features()
        # self._extract_subject_features()
        features = {
            "body_cap_max": self.body_cap_max,
            "body_cap_pct": self.body_cap_pct,
            "body_has_html": self.body_has_html,
            "body_nonascii_pct": self.body_nonascii_pct,
            "body_tokens": self.body_tokens,
            #    "body_urls": self.body_urls,
            #    "body_emails": self.body_emails,
            #    "subject_tokens": self.subject_tokens,
        }
        for char, pct in self.body_special_char_pct.items():
            features.update({f"body_ch{char}_pct": pct})
        return features

    def _fix_unicode(self, text):
        return ftfy.fix_text(text)
        #return unidecode.unidecode(cleaned_text)

    def _extract_body_features(self):
        message_subject = self.mailparser_obj.headers.get("Subject")
        if message_subject is None:
            message_subject = ""
        message_body = message_subject + "\n" + self.mailparser_obj.body

        body_urls = []
        if re.match(r"<\/?[a-zA-Z]*>", message_body) is not None:
            self.body_has_html = True
            soup = BeautifulSoup(message_body, "html.parser")
            for link in soup.find_all("a", href=True):
                for token in urlparse(link["href"]).netloc.split("."):
                    body_urls.append(token)

            message_body = soup.get_text(separator=" ")

        body_char_len = len(message_body)
        if body_char_len == 0:
            return None

        num_non_ascii = 0
        for char in message_body:
            if ord(char) > 128:
                num_non_ascii += 1

        self.body_nonascii_pct = num_non_ascii / body_char_len
        message_body = self._fix_unicode(message_body)
        for char in self.special_chars:
            self.body_special_char_pct.update(
                {f"ch{char}": message_body.count(char) / body_char_len}
            )

        self.body_cap_max, self.body_cap_pct = self._count_capital_sequences(
            message_body
        )

        message_body = re.sub(r"[-\[\]{}()<>#$^&*_+=|\\'\"]", " ", message_body)

        body_nlp = nlp(message_body)
        body_tokens = []
        # body_emails = []
        for token in body_nlp:
            if (
                not token.is_punct
                and not token.is_space
                and token.is_alpha
                and not token.is_stop
            ):
                body_tokens.append(token.lemma_)
            elif token.like_url:
                for fragment in urlparse(token.text).netloc.split("."):
                    body_tokens.append(fragment)

            elif token.like_email:
                for match in re.finditer(r"[^@]+$", token.text):
                    body_tokens.append(match.group())

        self.body_tokens = " ".join(body_tokens)
        # self.body_urls = " ".join(body_urls)
        # self.body_emails = " ".join(body_emails)

# TODO: fix this   
#    @property.getter
#    def label(self):
#        return self.label

#    @property.getter
#    def text(self):
#        return self.mailparser_obj.body

    def _count_capital_sequences(self, text):
        caps = re.finditer(r"[A-Z]{2,}.*?(?=(?:\W?[A-Z]?[a-z]|$))", text)
        cap_lengths = []
        for match in caps:
            cap_lengths.append(len(match.group()))
        if len(cap_lengths) == 0:
            return 0, 0
        cap_lengths = np.array(cap_lengths)
        cap_max = cap_lengths.max()
        cap_pct = cap_lengths.sum() / len(text)
        return cap_max, cap_pct
