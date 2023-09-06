import yaml
import json
from .train_test.exceptions import LoadingYamlFileException
from .train_test.detectors.overlap import DuplicateDetector
from .train_test.detectors.unknown_token import UnknownTokenDetector
from .train_test.utils import CompareUtil, get_str, parse_int_or_float
from .train_test.training_yaml_validator import YamlParser
from .train_test.detectors.text_complexity import TextComplexityAnalyzer

SAMPLE_DATASET_URL = (
    "https://censiusdev0public.blob.core.windows.net/demo-csvs/sample_data_training.csv"
)


class TrainTestValidator:
    def __init__(self, file_path=None):
        self.training_sentences = []
        self.test_sentences = []
        self.preprocess_args = {}
        self.rules_data = None
        self.violations = {}
        self.information = {}
        if file_path is not None:
            self.load_data_from_yaml(file_path)
        else:
            self.execut_default_rules()

    def quick_run_dataset(self, rules_file_path=None):
        import pandas as pd

        print("Getting sample dataset")
        df = pd.read_csv(SAMPLE_DATASET_URL)
        print("Dataset Download Completed")
        sentences = df["highlights"].tolist()
        self.training_sentences = sentences[:900]
        self.test_sentences = sentences[750:]
        print("Sample test and training sentences are set")
        if rules_file_path is not None:
            print("Loading rules file")
            self.load_data_from_yaml(rules_file_path)
        else:
            self.execut_default_rules()
        print("Running Train test Validations")
        self.validate(self.training_sentences, self.test_sentences)

    def execut_default_rules(self):
        from .train_test.sample_rules_data import rules_data

        self.rules_data = rules_data
        self.validate_rules_json()
        print("Default Rules Data loaded successfully as no file was passed.")

    def load_data_from_yaml(self, file_path):
        try:
            with open(file_path, "r") as file:
                self.rules_data = yaml.safe_load(file)
                self.validate_rules_json()
                print(f"Data loaded from '{file_path}' successfully.")
        except FileNotFoundError:
            raise LoadingYamlFileException(f"File '{file_path}' not found.")
        except yaml.YAMLError as e:
            raise LoadingYamlFileException("Error while parsing YAML:", e)

    def validate_rules_json(self):
        YamlParser.validate_yaml_json(self.rules_data)

    def validate_range_rules(self, rule, rulename, key, val):
        if "gt" in rule and CompareUtil.lte(val, rule["gt"]):
            self.violations[key].append(f" gt: {get_str(rule['gt'],val, rulename)}")
        if "lt" in rule and CompareUtil.gte(val, rule["lt"]):
            self.violations[key].append(f"lt: {get_str(rule['lt'],val,rulename)}")
        if "gte" in rule and CompareUtil.lt(val, rule["gte"]):
            self.violations[key].append(f"gte:{get_str(rule['gte'],val,rulename)}")
        if "lte" in rule and CompareUtil.gt(val, rule["lte"]):
            self.violations[key].append(f"lte : {get_str(rule['lte'],val,rulename)}")

    def validate(self, training_sentences, test_sentences):
        if "detect_duplicates" in self.rules_data:
            self.violations["detect_duplicates"] = []
            detector = DuplicateDetector(
                training_sentences,
                test_sentences,
                **self.rules_data["detect_duplicates"][0]["params"]["preprocess_args"],
            )
            percentage = parse_int_or_float(
                "{:.2f}".format(detector.calculate_exact_match_percentage())
            )

            self.validate_range_rules(
                self.rules_data["detect_duplicates"][0]["params"]["threshold"],
                "detect_duplicates",
                "detect_duplicates",
                percentage,
            )
        if "detect_unknown_tokens" in self.rules_data:
            self.violations["detect_unknown_tokens"] = []
            self.information["total_unknown_tokens"] = []
            detector = UnknownTokenDetector(
                training_sentences,
                **self.rules_data["detect_unknown_tokens"][0]["params"][
                    "preprocess_args"
                ],
            )
            (
                percentage,
                total_unknown_tokens,
            ) = detector.calculate_unknown_token_percentage(test_sentences)
            percentage = parse_int_or_float("{:.2f}".format(percentage))
            self.validate_range_rules(
                self.rules_data["detect_unknown_tokens"][0]["params"]["threshold"],
                "detect_unknown_tokens",
                "detect_unknown_tokens",
                percentage,
            )
            if total_unknown_tokens > 100:
                file_name = detector.write_tokens()

                self.information["total_unknown_tokens"].append(
                    f"info : unknown tokens written to {file_name}"
                )
            else:
                self.information["total_unknown_tokens"].append(
                    list(detector.unknown_tokens)
                )

        if "text_complexity_distribution" in self.rules_data:
            training_analyzer = TextComplexityAnalyzer(training_sentences)
            test_analyzer = TextComplexityAnalyzer(test_sentences)
            training_distribution = (
                training_analyzer.calculate_complexity_distribution()
            )
            test_distribution = test_analyzer.calculate_complexity_distribution()
            threshold_percentage = self.rules_data["text_complexity_distribution"][0][
                "params"
            ]["threshold"]
            differences, info = TextComplexityAnalyzer.compare_distributions(
                training_distribution, test_distribution, threshold_percentage
            )
            print(
                "Text Complexity differences greater than", threshold_percentage, "%:"
            )
            print(f"{'class':<15}{'Training %':<15}{'Test %':<10}{'Diff %':<10}")
            print("-" * 55)

            for (
                category,
                training_percentage,
                test_percentage,
                difference,
            ) in differences:
                print(
                    f"{category:<15}{training_percentage:>10.2f}%{test_percentage:>13.2f}%{difference:>13.2f}%"
                )

            print("*" * 55)

            print("Text Complexity other classes")
            print(f"{'class':<15}{'Training %':<15}{'Test %':<13}{'Diff %':<13}")
            print("-" * 55)

            for (
                category,
                training_percentage,
                test_percentage,
                difference,
            ) in info:
                print(
                    f"{category:<15}{training_percentage:<10.2f}%{test_percentage:>13.2f}%{difference:>13.2f}%"
                )
        self.print_violations()

    def print_violations(self):
        pretty_json = json.dumps(self.information, indent=4)
        print("\nInformation on Violations")
        print(pretty_json)

        pretty_json = json.dumps(self.violations, indent=4)
        print("\nTotal Violations found")
        print(pretty_json)
