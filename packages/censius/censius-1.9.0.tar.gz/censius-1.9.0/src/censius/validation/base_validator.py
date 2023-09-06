import yaml
import json
from elemeta.nlp.metafeature_extractors_runner import (
    MetafeatureExtractorsRunner,
    SentimentPolarity,
    HintedProfanityWordsCount,
)
from .exceptions import LoadingYamlFileException, ExpectedKeysMissingException
from .yaml_validator import YamlParser
from .utils import parse_int_or_float, CompareUtil, get_str


class Validator:
    def __init__(self):
        self.rules_data = None
        self.violations = {}
        self.mode = None
        self.required_fields = []

    def load_data_from_yaml(self, file_path, mode):
        try:
            with open(file_path, "r") as file:
                self.rules_data = yaml.safe_load(file)
                self.mode = mode
                self.required_fields = (
                    self.rules_data["required_fields"]
                    if "required_fields" in self.rules_data
                    else None
                )
                self.validate_rules_json()
                print(f"Data loaded from '{file_path}' successfully.")
        except FileNotFoundError:
            raise LoadingYamlFileException(f"File '{file_path}' not found.")
        except yaml.YAMLError as e:
            raise LoadingYamlFileException("Error while parsing YAML:", e)

    def validate_rules_json(self):
        YamlParser.validate_yaml_json(self.rules_data)

    def validate_choice(self, rule, data, key):
        if data not in rule:
            self.violations[key].append(
                f"{self.mode} value not in expected choices rule violated"
            )

    def validate_datatype(self, rule, data, key):
        if rule == "string" and not isinstance(data, str):
            self.violations[key].append(
                f"{self.mode} value datatype string rule violated"
            )
        if rule == "boolean" and not isinstance(data, bool):
            self.violations[key].append(
                f"{self.mode} value datatype boolean rule violated"
            )
        if rule == "integer" and not isinstance(data, int):
            self.violations[key].append(
                f"{self.mode} value datatype integer rule violated"
            )
        if rule == "float" and not isinstance(data, float):
            self.violations[key].append(
                f"{self.mode} value datatype float rule violated"
            )

    def validate_range_rules(self, rule, rulename, key, val):
        if "gt" in rule and CompareUtil.lte(val, rule["gt"]):
            self.violations[key].append(
                f"{self.mode} value gt: {get_str(rule['gt'],val, rulename)}"
            )
        if "lt" in rule and CompareUtil.gte(val, rule["lt"]):
            self.violations[key].append(
                f"{self.mode} value  lt: {get_str(rule['lt'],val,rulename)}"
            )
        if "gte" in rule and CompareUtil.lt(val, rule["gte"]):
            self.violations[key].append(
                f"{self.mode} value  gte:{get_str(rule['gte'],val,rulename)}"
            )
        if "lte" in rule and CompareUtil.gt(val, rule["lte"]):
            self.violations[key].append(
                f"{self.mode} value lte : {get_str(rule['lte'],val,rulename)}"
            )

    def validate_range(self, rule, data, key):
        val = parse_int_or_float(data)
        self.validate_range_rules(rule, "range", key, val)

    def validate_len(self, rule, data, key):
        val = len(data)
        self.validate_range_rules(rule, "length", key, val)

    def validate_text_complexity(self, rule, data, key):
        metafeature_extractors_runner = MetafeatureExtractorsRunner()
        features = metafeature_extractors_runner.run(data)
        val = features["text_complexity"]
        self.validate_range_rules(rule, "text complexity", key, val)

    def validate_sentiment_polarity(self, rule, data, key):
        sp = SentimentPolarity()
        val = sp(data)
        self.validate_range_rules(rule, "sentiment polarity", key, val)

    def validate_profanity(self, rule, data, key):
        metafeature_extractors_runner = MetafeatureExtractorsRunner()
        features = metafeature_extractors_runner.run(data)
        hpwc = HintedProfanityWordsCount()
        val = parse_int_or_float(
            "{:.2f}".format((hpwc(data) / features["word_count"]) * 100)
        )
        self.validate_range_rules(rule, "text profanity", key, val)

    def req_key_validate(self, rule, data, key):
        rule_set = set(rule)
        data_set = set(data.keys())
        if not rule_set.issubset(data_set):
            notfound = ",".join(rule_set.difference(data_set))
            self.violations[key].append(
                f"{self.mode} violation , mandatory keys in data not found"
            )
            raise ExpectedKeysMissingException(
                f"{self.mode} violation,{notfound} missing in {self.mode}"
            )

    def print_violations(self):
        pretty_json = json.dumps(self.violations, indent=4)
        print("Total Violations found")
        print(pretty_json)
