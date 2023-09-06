from pydantic import ValidationError
from censius.validation.utils import RangeValid
from censius.validation.exceptions import (
    InvalidYamlKeyException,
    RequiredKeyMissingException,
    InvalidChoiceForBooleanException,
    RangeValueExceptions,
)
from censius.validation.train_test.rules_constants import (
    RANGE_ATTRIBUTES,
    RANGE_DTYPES,
    ALLOWED_RULES,
    MANDATORY_ATTRIBUTES,
    ALLOWED_ATTRIBUTES_RULES,
    PREPROCESSING_RULES,
    BOOLEAN_ATTRIBUTES,
)


class YamlParser:
    @staticmethod
    def validate_range_values(data, rule_key):
        try:
            RangeValid(**data)
        except ValidationError:
            raise RangeValueExceptions(
                f"Range should be valid integer,float for {rule_key} : {data}"
            )

    @staticmethod
    def validate_range_rule(rule_key, rule_value, key):
        if rule_key in RANGE_DTYPES:
            if not isinstance(rule_value, dict) or not set(rule_value.keys()).issubset(
                RANGE_ATTRIBUTES
            ):
                raise InvalidYamlKeyException(
                    f"Invalid format for {key} rule {rule_key}:{rule_value}"
                )
            YamlParser.validate_range_values(rule_value, rule_key)

    @staticmethod
    def validate_preprocess_args(rule_key, rule_value, key):
        if rule_key in PREPROCESSING_RULES:
            if not set(rule_value.keys()).issubset(set(ALLOWED_ATTRIBUTES_RULES[key])):
                raise InvalidYamlKeyException(
                    f"Invalid attribute for {key}:- preprocess_args:{rule_value}"
                )
            for key, value in rule_value.items():
                if key in BOOLEAN_ATTRIBUTES and not {value}.issubset({True, False}):
                    raise InvalidChoiceForBooleanException(
                        f"for {key} available choices are [True,False] given {value}"
                    )

    @staticmethod
    def validate_yaml_json(rules_data):
        rules_defined = set(rules_data.keys())
        if not rules_defined.issubset(ALLOWED_RULES):
            raise InvalidYamlKeyException(
                f"{rules_defined - ALLOWED_RULES} are not allowed rules"
            )
        for key, value in rules_data.items():
            for rule_param in value:
                if "params" not in rule_param.keys():
                    raise InvalidYamlKeyException(
                        "params key not found failed to parse rules"
                    )
                if set(rule_param["params"].keys()) != MANDATORY_ATTRIBUTES:
                    raise RequiredKeyMissingException(
                        "preprocess_args and threshold must be specified"
                    )
                for rule_key, rule_value in rule_param["params"].items():
                    YamlParser.validate_range_rule(rule_key, rule_value, key)
                    YamlParser.validate_preprocess_args(rule_key, rule_value, key)
