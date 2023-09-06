import json


def _pformat(obj, indentation_level):
    indentation_count = 4
    formatted_result = ""
    if isinstance(obj, dict):
        count = len(obj) - 1
        formatted_result += "{\n"
        for index, (key, value) in enumerate(obj.items()):
            formatted_result += f"""{
            " " * ((indentation_level + 1) * indentation_count)
            }{
            json.dumps(key, ensure_ascii=False)
            }: {
            _pformat(value, indentation_level + 1)
            }{
            "," if index < count else ""
            }\n"""
        formatted_result += f"""{
        " " * (indentation_level * indentation_count)
        }}}"""
    elif isinstance(obj, list):
        count = len(obj) - 1
        formatted_result += "[\n"
        for index, value in enumerate(obj):
            formatted_result += f"""{
            " " * ((indentation_level + 1) * indentation_count)
            }{
            _pformat(value, indentation_level + 1)
            }{
            "," if index < count else ""
            }\n"""
        formatted_result += f"""{
        " " * (indentation_level * indentation_count)
        }]"""
    elif isinstance(obj, str) or obj in [None, True, False]:
        formatted_result += json.dumps(obj, ensure_ascii=False)
    else:
        formatted_result += repr(obj)
    return formatted_result


def pformat(obj):
    return _pformat(obj, 0)
