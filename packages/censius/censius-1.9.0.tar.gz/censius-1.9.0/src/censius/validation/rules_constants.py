ALLOWED_RULES = [
    "datatype",
    "len-validate",
    "choice-validate",
    "range-validate",
    "text-complexity-validate",
    "sentiment-polarity-validate",
    "profanity-validate",
]
RANGE_ATTRIBUTES = {"gt", "lt", "gte", "lte"}
RANGE_DTYPES = [
    "len-validate",
    "range-validate",
    "text-complexity-validate",
    "sentiment-polarity-validate",
    "profanity-validate",
]
DTYPES = ["string", "integer", "boolean", "float"]

ALLOWED_DTYPES_RULES = {
    "string": [
        "datatype",
        "len-validate",
        "choice-validate",
        "text-complexity-validate",
        "sentiment-polarity-validate",
        "profanity-validate",
    ],
    "integer": ["datatype", "range-validate"],
    "boolean": ["datatype", "choice-validate"],
    "float": ["datatype", "range-validate"],
}
