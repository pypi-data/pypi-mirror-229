import textstat
from collections import Counter
from concurrent.futures import ProcessPoolExecutor


class TextComplexityAnalyzer:
    def __init__(self, sentences):
        self.sentences = sentences

    @staticmethod
    def categorize_complexity(score):
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Confusing"

    @staticmethod
    def calculate_complexity(sentence):
        score = textstat.flesch_reading_ease(sentence)
        category = TextComplexityAnalyzer.categorize_complexity(score)
        return category

    def calculate_complexity_distribution(self):
        complexity_counter = Counter()
        total_sentences = len(self.sentences)

        with ProcessPoolExecutor() as executor:
            categories = list(executor.map(self.calculate_complexity, self.sentences))

        complexity_counter.update(categories)

        distribution_percentage = {
            category: count / total_sentences * 100
            for category, count in complexity_counter.items()
        }
        return distribution_percentage

    @staticmethod
    def compare_distributions(training_distribution, test_distribution, threshold):
        result = []
        info = []

        for category in training_distribution:
            training_percentage = training_distribution.get(category, 0)
            test_percentage = test_distribution.get(category, 0)

            difference = abs(training_percentage - test_percentage)
            if "gt" in threshold and difference > threshold["gt"]:
                result.append(
                    (category, training_percentage, test_percentage, difference)
                )
            elif "lt" in threshold and difference < threshold["lt"]:
                result.append(
                    (category, training_percentage, test_percentage, difference)
                )
            elif "gte" in threshold and difference >= threshold["gte"]:
                result.append(
                    (category, training_percentage, test_percentage, difference)
                )
            elif "lte" in threshold and difference <= threshold["lte"]:
                result.append(
                    (category, training_percentage, test_percentage, difference)
                )
            else:
                info.append(
                    (category, training_percentage, test_percentage, difference)
                )

        return result, info
