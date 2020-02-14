def calculate_bytes(item: dict) -> int:
    return sum(_calc_attr(v) + len(k) for k, v in _serialize(item).items())


def calculate_kbytes(item: dict) -> float:
    return calculate_bytes(item) / 1024


def _calc_attr(attr: dict) -> int:
    if 'B' in attr:
        return _calc_binary(attr['B'])

    if 'BOOL' in attr:
        return 1

    if 'BS' in attr:
        return sum(_calc_binary(b) for b in attr['BS'])

    if 'L' in attr:
        return sum(_calc_attr(i) + 1 for i in attr['L']) + 3

    if 'M' in attr:
        return sum(_calc_attr(v) + len(k) + 1 for k, v in attr['M'].items()) + 3

    if 'N' in attr:
        return _calc_number(attr['N'])

    if 'NS' in attr:
        return sum(_calc_number(n) for n in attr['NS'])

    if 'NULL' in attr:
        return 1

    if 'S' in attr:
        return _calc_string(attr['S'])

    if 'SS' in attr:
        return sum(_calc_string(s) for s in attr['SS'])

    raise Exception(f'invalid "{attr}" data type')


def _calc_binary(b: str) -> int:
    from base64 import b64decode
    return len(b64decode(b))


def _calc_number(n: str) -> int:
    from math import ceil
    return ceil(len(n) / 2) + 1


def _calc_string(s: str) -> int:
    return len(s)


def _serialize(item: dict) -> dict:
    from boto3 import resource
    from boto3.dynamodb.types import TypeSerializer

    resource('dynamodb')

    serializer = TypeSerializer()
    serialized = {k: serializer.serialize(v) for k, v in item.items()}

    return serialized

