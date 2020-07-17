a = '''"Some text"'''
b = '''f"Some text"'''


entry_points_1 = {
        'autopep8_quotes.formatter': [  # noqa
            "lowercase_string_prefix = autopep8_quotes.modules.formater.lowercase_string_prefix:formatter",
    ],
}

entry_points_2 = {
    "autopep8_quotes.formatter": [  # another comment
        "lowercase_string_prefix = autopep8_quotes.modules.formater.lowercase_string_prefix:formatter",
    ],
}

entry_points_2 = {
    "autopep8_quotes.formatter": [
        "lowercase_string_prefix = autopep8_quotes.modules.formater.lowercase_string_prefix:formatter",
    ],
}
