from concurrent.futures import ProcessPoolExecutor
from functools import partial
from .preprocessing_functions import preprocess_sentence


class DuplicateDetector:
    def __init__(self, training_sentences, test_sentences, **preprocess_args):
        self.training_sentences = training_sentences
        self.test_sentences = test_sentences
        self.preprocess_args = preprocess_args

    def process_sentence(self, sentence, preprocess_func):
        return preprocess_func(sentence)

    def process_sentences(self, sentences, preprocess_func):
        with ProcessPoolExecutor() as executor:
            processed_sentences = list(
                executor.map(
                    self.process_sentence, sentences, [preprocess_func] * len(sentences)
                )
            )
        return processed_sentences

    def calculate_exact_match_percentage(self):
        preprocess_func = partial(preprocess_sentence, **self.preprocess_args)

        preprocessed_test = self.process_sentences(self.test_sentences, preprocess_func)
        preprocessed_train = self.process_sentences(
            self.training_sentences, preprocess_func
        )

        test_set = set(preprocessed_test)
        training_set = set(preprocessed_train)

        common_sentences = test_set.intersection(training_set)

        total_test_samples = len(self.test_sentences)
        test_samples_in_train = len(common_sentences)

        percentage_in_train = (test_samples_in_train / total_test_samples) * 100
        return percentage_in_train
