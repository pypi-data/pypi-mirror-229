from censius.validation.base_validator import Validator


class InputValidator(Validator):
    def __init__(self, file_path):
        super().__init__()
        self.load_data_from_yaml(file_path, "input")

    def validate_format(self, data):
        if "format-rules" in self.rules_data:
            for rule in self.rules_data["format-rules"]:
                for key, value in rule.items():
                    self.violations[key] = []
                    if "key-validate" == key:
                        self.req_key_validate(value, data, key)

    def validate(self, data):
        self.validate_format(data)
        for rule in self.rules_data["validation-rules"]:
            for key, value in rule.items():
                self.violations[key] = []
                for rule_params in value:
                    for rule_key, rule_value in rule_params.items():
                        if "datatype" == rule_key:
                            self.validate_datatype(rule_value, data[key], key)
                        if "range-validate" == rule_key:
                            self.validate_range(rule_value, data[key], key)
                        if "len-validate" == rule_key:
                            self.validate_len(rule_value, data[key], key)
                        if "choice-validate" == rule_key:
                            self.validate_choice(rule_value, data[key], key)
                        if "text-complexity-validate" == rule_key:
                            self.validate_text_complexity(rule_value, data[key], key)
                        if "sentiment-polarity-validate" == rule_key:
                            self.validate_sentiment_polarity(rule_value, data[key], key)
                        if "profanity-validate" == rule_key:
                            self.validate_profanity(rule_value, data[key], key)

        self.print_violations()


class OutputValidator(Validator):
    def __init__(self, file_path):
        super().__init__()
        self.load_data_from_yaml(file_path)

    def validate_format(self, data):
        if "format-rules" in self.rules_data:
            for rule in self.rules_data["format-rules"]:
                for key, value in rule.items():
                    self.violations[key] = []
                    if "key-validate" == key:
                        self.req_key_validate(value, data, key)
                    if "pii-masking" == key:
                        self.req_pii_masking(value, data, key)

    def validate(self, data):
        self.validate_format(data)
        for rule in self.rules_data["validation-rules"]:
            for key, value in rule.items():
                self.violations[key] = []
                for rule_params in value:
                    for rule_key, rule_value in rule_params.items():
                        if "datatype" == rule_key:
                            self.validate_datatype(rule_value, data[key], key)
                        if "range-validate" == rule_key:
                            self.validate_range(rule_value, data[key], key)
                        if "len-validate" == rule_key:
                            self.validate_len(rule_value, data[key], key)
                        if "choice-validate" == rule_key:
                            self.validate_choice(rule_value, data[key], key)
                        if "text-complexity-validate" == rule_key:
                            self.validate_text_complexity(rule_value, data[key], key)
                        if "sentiment-polarity-validate" == rule_key:
                            self.validate_sentiment_polarity(rule_value, data[key], key)
                        if "profanity-validate" == rule_key:
                            self.validate_profanity(rule_value, data[key], key)
        self.print_violations()
