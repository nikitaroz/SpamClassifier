import re

import ftfy
import mailparser
import numpy as np
import spacy
from bs4 import BeautifulSoup
from matplotlib.cm import ScalarMappable, get_cmap
from matplotlib.colors import Normalize, to_hex

# pylint: disable=no-name-in-module
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex, compile_prefix_regex, compile_suffix_regex


# https://spacy.io/usage/linguistic-features#native-tokenizers
# https://stackoverflow.com/questions/56439423/spacy-parenthesis-tokenization-pairs-of-lrb-rrb-not-tokenized-correctly
def custom_tokenizer(nlp_):
    infixes = [r"\b\)\b", r"\b\(\b"] + nlp_.Defaults.infixes
    infix_re = compile_infix_regex(infixes)
    prefix_re = compile_prefix_regex(nlp_.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp_.Defaults.suffixes)
    return Tokenizer(
        nlp_.vocab,
        prefix_search=prefix_re.search,
        suffix_search=suffix_re.search,
        infix_finditer=infix_re.finditer,
        token_match=None,
    )


nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner", "textcat"])
nlp.tokenizer = custom_tokenizer(nlp)


class Message:
    def __init__(
        self, parser: mailparser.MailParser, tokenizer=spacy.load("en_core_web_sm")
    ):
        self.parser = parser
        self._body = ftfy.fix_text(self.parser.body)
        self._subject = ftfy.fix_text(parser.headers.get("Subject", ""))

        self.tokenizer = tokenizer

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

        doc = self.tokenizer(normalized_text)
        filtered_tokens = []
        # TODO: further cleaning is needed here
        for token in doc:
            if (
                token.is_space
                or token.is_digit
                or token.is_stop
                or token.is_punct
            ):
                continue
            else:
                filtered_tokens.append(token.lemma_.lower())
        return " ".join(filtered_tokens)

    def subject_html(self, db_connector=None, scalar_map=None):
        return self._get_html(self.subject, db_connector, scalar_map)

    def body_html(self, db_connector=None, scalar_map=None):
        return self._get_html(self.body, db_connector, scalar_map)

    def _get_html(self, text, db_connector, scalar_map):
        tokens = []
        if scalar_map is None:
            norm = Normalize(vmin=-20, vmax=20)
            cmap = get_cmap("coolwarm")
            scalar_map = ScalarMappable(norm=norm, cmap=cmap)
        for token in self.tokenizer(text):
            if (
                token.is_space
                or token.is_digit
                or token.is_stop
                or token.is_punct
                or token.is_digit
            ):
                tokens.append(token.text + token.whitespace_)
            elif token.text == "\n":
                tokens.append("<br>")
            else:
                if db_connector is not None:
                    coef = db_connector.cursor.execute(
                        "SELECT coefficient FROM features WHERE feature == ?",
                        (token.lemma_,),
                    ).fetchone()
                    if coef is not None:
                        color = to_hex(scalar_map.to_rgba(coef[0]))
                        tokens.append(
                            f"<mark style='background-color:{color};'>"
                            + token.text
                            + "</mark>"
                            + token.whitespace_
                        )
                    else:
                        tokens.append(token.text + token.whitespace_)

        tokens = "".join(tokens)
        return tokens
