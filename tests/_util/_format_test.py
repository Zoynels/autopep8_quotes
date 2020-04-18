
import pytest  # type: ignore


@pytest.mark.basic  # type: ignore
def test__isevaluatable():
    import autopep8_quotes._util._format as util_format
    assert (True, 'Some " text') == util_format.isevaluatable("""'Some " text'""", "")
    assert (True, 'Some " text') == util_format.isevaluatable("""f'Some " text'""", "f")


@pytest.mark.basic  # type: ignore
def test__save_values_to_file() -> None:
    import datetime
    from types import SimpleNamespace
    import autopep8_quotes._util._format as util_format

    args = SimpleNamespace()
    args._datetime_start = datetime.datetime.now()
    args.save_values_to_file = True

    token_dict1 = {}
    token_dict1["filename"] = "filename"
    token_dict1["pos1"] = "pos1"
    token_dict1["token_string"] = "token_string"

    token_dict2 = {}
    token_dict2["filename"] = b"filename"
    token_dict2["pos1"] = b"pos1"
    token_dict2["token_string"] = b"token_string"

    token_dict3 = {}
    token_dict3["filename"] = r"filename"
    token_dict3["pos1"] = r"pos1"
    token_dict3["token_string"] = r"token_string"

    input_list = [token_dict1, token_dict2, token_dict3]

    util_format.save_values_to_file(args=args, input_list=input_list, name="test")
