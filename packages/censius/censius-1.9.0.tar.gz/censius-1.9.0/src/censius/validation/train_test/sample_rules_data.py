rules_data = {
    "detect_duplicates": [
        {
            "params": {
                "preprocess_args": {
                    "ignore_case": True,
                    "remove_punctuation": True,
                    "normalize_unicode": True,
                    "remove_stopwords": True,
                },
                "threshold": {"lte": 15},
            }
        }
    ],
    "detect_unknown_tokens": [
        {
            "params": {
                "preprocess_args": {
                    "remove_punctuation": True,
                    "remove_stopwords": True,
                    "do_lemmatization": True,
                },
                "threshold": {"lte": 15},
            }
        }
    ],
    "text_complexity_distribution": [
        {
            "params": {
                "preprocess_args": {},
                "threshold": {"gte": 25},
            }
        }
    ],
}
