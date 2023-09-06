import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import words
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from multiprocessing import Pool, cpu_count
import string
import time
import re

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("words", quiet=True)


def check_string_digits(input_string):
    if re.match(r"^\d+$", input_string):
        return True
    elif re.search(r"\d", input_string):
        return True
    else:
        return False


class UnknownTokenDetector:
    def __init__(self, training_sentences, **preprocess_args):
        train_vocab = set(words.words())  # Vocabulary from NLTK corpus
        self.stop_words = set(stopwords.words("english"))
        for sent in training_sentences:
            sent = sent.translate(str.maketrans("", "", string.punctuation))
            words_in_sent = word_tokenize(sent.lower())
            for word in words_in_sent:
                if word not in self.stop_words and not check_string_digits(word):
                    train_vocab.add(word)

        self.train_vocab = train_vocab
        self.preprocess_args = preprocess_args or {}
        self.lemmatizer = WordNetLemmatizer()
        self.unknown_tokens = set()
        self.filtered_tokens = set()

    def write_tokens(self):
        fname = f"tokens_{time.time_ns()}.txt"
        with open(fname, "w") as f:
            f.write("\n".join(list(self.unknown_tokens)))
        return fname

    def calculate_unknown_token_percentage(self, test_sentences):
        with Pool(cpu_count()) as pool:
            results = pool.map(self.process_sentence, test_sentences)

        for result in results:
            self.unknown_tokens.update(result[0])
            self.filtered_tokens.update(result[1])

        total_unknown_tokens = len(set(self.unknown_tokens))
        total_tokens = len(self.filtered_tokens)

        total_unknown_percentage = (
            (total_unknown_tokens / total_tokens) * 100 if total_tokens else 0
        )
        return total_unknown_percentage, total_unknown_tokens

    def process_sentence(self, sentence):
        if self.preprocess_args.get("remove_punctuation", True):
            sentence = sentence.translate(str.maketrans("", "", string.punctuation))

        tokens = word_tokenize(sentence)

        filtered_tokens = [
            self.lemmatizer.lemmatize(token)
            if self.preprocess_args.get("do_lemmatization", False)
            else token
            for token in tokens
            if self.preprocess_args.get("remove_stopwords", True)
            and token.lower() not in self.stop_words
            and not check_string_digits(token)
        ]

        unknown_tokens = [
            token for token in filtered_tokens if token.lower() not in self.train_vocab
        ]
        return unknown_tokens, filtered_tokens
