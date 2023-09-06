ALLOWED_RULES = {
    "detect_duplicates",
    "detect_unknown_tokens",
    "text_complexity_distribution",
}
RANGE_ATTRIBUTES = {"gt", "lt", "gte", "lte"}
RANGE_DTYPES = ["threshold"]
PREPROCESSING_RULES = ["preprocess_args"]
MANDATORY_ATTRIBUTES = {"preprocess_args", "threshold"}
ALLOWED_ATTRIBUTES_RULES = {
    "detect_duplicates": [
        "ignore_case",
        "remove_punctuation",
        "normalize_unicode",
        "remove_stopwords",
    ],
    "detect_unknown_tokens": [
        "do_lemmatization",
        "remove_punctuation",
        "remove_stopwords",
    ],
    "text_complexity_distribution": [],
}

BOOLEAN_ATTRIBUTES = [
    "ignore_case",
    "remove_punctuation",
    "normalize_unicode",
    "remove_stopwords",
]
