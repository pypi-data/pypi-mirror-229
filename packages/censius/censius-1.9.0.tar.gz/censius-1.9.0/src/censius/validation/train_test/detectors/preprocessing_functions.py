import string
import unicodedata
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)

stopwords = set(stopwords.words("english"))


def preprocess_sentence(
    sentence,
    ignore_case=True,
    remove_punctuation=True,
    normalize_unicode=True,
    remove_stopwords=True,
):
    if ignore_case:
        sentence = sentence.lower()
    if remove_punctuation:
        sentence = sentence.translate(str.maketrans("", "", string.punctuation))
    if normalize_unicode:
        sentence = (
            unicodedata.normalize("NFKD", sentence)
            .encode("ASCII", "ignore")
            .decode("utf-8")
        )
    if remove_stopwords:
        sentence_tokens = sentence.split()
        sentence_tokens = [
            token for token in sentence_tokens if token.lower() not in stopwords
        ]
        sentence = " ".join(sentence_tokens)
    return sentence
