import json
from pydantic import ValidationError
from censius.validation.utils import RangeValid
from censius.validation.exceptions import (
    InvalidYamlKeyException,
    RequiredKeyMissingException,
    DatatypeFirstRuleException,
    InvalidRuleForDtypeException,
    InvalidChoiceForBooleanException,
    RangeValueExceptions,
)
from censius.validation.rules_constants import (
    DTYPES,
    RANGE_ATTRIBUTES,
    RANGE_DTYPES,
    ALLOWED_RULES,
    ALLOWED_DTYPES_RULES,
)


class YamlParser:
    key_dtype = {}

    @staticmethod
    def validate_datatype_rule(rule_key, rule_value, key):
        if "datatype" == rule_key and (
            not isinstance(rule_value, str) or rule_value not in DTYPES
        ):
            raise InvalidYamlKeyException(
                f"Invalid value for {key} rule {rule_key}:{rule_value}"
            )

    @staticmethod
    def validate_choice_rule(rule_key, rule_value, key):
        if "choice-validate" == rule_key:
            if not isinstance(rule_value, list):
                raise InvalidYamlKeyException(
                    f"Invalid value for {key} rule {rule_key}:{rule_value}"
                )
            if YamlParser.key_dtype[key] == "boolean" and not set(rule_value).issubset(
                {True, False}
            ):
                raise InvalidChoiceForBooleanException(
                    f"for {key} available choices are [True,False] given {rule_value}"
                )

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
    def validate_allow_rule(rule_key, key):
        if rule_key not in ALLOWED_RULES:
            raise InvalidYamlKeyException(f"Invalid rule for {key}:- {rule_key}")
        dtype = YamlParser.key_dtype[key]
        if rule_key not in ALLOWED_DTYPES_RULES[dtype]:
            raise InvalidRuleForDtypeException(
                f"{key}:-{rule_key} rule invalid for {dtype} datatype"
            )

    @staticmethod
    def check_datatype_exists(rule_value, key):
        if "datatype" not in json.dumps(rule_value):
            raise RequiredKeyMissingException(
                f"datatype missing for rule {key}:{rule_value}"
            )
        if "datatype" not in rule_value[0]:
            raise DatatypeFirstRuleException(f"datatype must be first rule for {key}")
        YamlParser.key_dtype[key] = rule_value[0]["datatype"]

    @staticmethod
    def validate_yaml_json(rules_data):
        if "validation-rules" not in rules_data.keys():
            raise InvalidYamlKeyException(
                "validation_rules key not found failed to parse rules"
            )
        for rule in rules_data["validation-rules"]:
            for key, value in rule.items():
                YamlParser.check_datatype_exists(value, key)

                for rule_params in value:
                    for rule_key, rule_value in rule_params.items():
                        YamlParser.validate_allow_rule(rule_key, key)
                        YamlParser.validate_datatype_rule(rule_key, rule_value, key)
                        YamlParser.validate_range_rule(rule_key, rule_value, key)
                        YamlParser.validate_choice_rule(rule_key, rule_value, key)
