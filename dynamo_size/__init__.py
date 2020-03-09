import collections.abc
import decimal

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
    serializer = TypeSerializer()
    serialized = {k: serializer.serialize(v) for k, v in item.items()}

    return serialized


# https://github.com/boto/boto3/blob/8e713130343a784fd4e38de3986b38e87a352f22/boto3/dynamodb/types.py#L33
_context = decimal.Context(
    Emin=-128, Emax=126, prec=38,
    traps=[decimal.Clamped, decimal.Overflow, decimal.Inexact, decimal.Rounded, decimal.Underflow])


# https://github.com/boto/boto3/blob/8e713130343a784fd4e38de3986b38e87a352f22/boto3/dynamodb/types.py#L72
class TypeSerializer(object):
    def serialize(self, value):
        dynamodb_type = self._get_dynamodb_type(value)
        serializer = getattr(self, '_serialize_%s' % dynamodb_type.lower())
        return {dynamodb_type: serializer(value)}

    def _get_dynamodb_type(self, value):
        dynamodb_type = None

        # https://github.com/boto/boto3/blob/8e713130343a784fd4e38de3986b38e87a352f22/boto3/dynamodb/types.py#L21
        if self._is_null(value):
            dynamodb_type = 'NULL'

        elif self._is_boolean(value):
            dynamodb_type = 'BOOL'

        elif self._is_number(value):
            dynamodb_type = 'N'

        elif self._is_string(value):
            dynamodb_type = 'S'

        elif self._is_binary(value):
            dynamodb_type = 'B'

        elif self._is_type_set(value, self._is_number):
            dynamodb_type = 'NS'

        elif self._is_type_set(value, self._is_string):
            dynamodb_type = 'SS'

        elif self._is_type_set(value, self._is_binary):
            dynamodb_type = 'BS'

        elif self._is_map(value):
            dynamodb_type = 'M'

        elif self._is_list(value):
            dynamodb_type = 'L'

        else:
            msg = 'Unsupported type "%s" for value "%s"' % (type(value), value)
            raise TypeError(msg)

        return dynamodb_type

    def _is_null(self, value):
        if value is None:
            return True
        return False

    def _is_boolean(self, value):
        if isinstance(value, bool):
            return True
        return False

    def _is_number(self, value):
        if isinstance(value, (int, decimal.Decimal)):
            return True
        elif isinstance(value, float):
            raise TypeError(
                'Float types are not supported. Use Decimal types instead.')
        return False

    def _is_string(self, value):
        if isinstance(value, str):
            return True
        return False

    def _is_binary(self, value):
        if isinstance(value, bytearray):
            return True
        elif isinstance(value, bytes):
            return True
        return False

    def _is_set(self, value):
        if isinstance(value, collections.abc.Set):
            return True
        return False

    def _is_type_set(self, value, type_validator):
        if self._is_set(value):
            if False not in map(type_validator, value):
                return True
        return False

    def _is_map(self, value):
        if isinstance(value, collections.abc.Mapping):
            return True
        return False

    def _is_list(self, value):
        if isinstance(value, list):
            return True
        return False

    def _serialize_null(self, value):
        return True

    def _serialize_bool(self, value):
        return value

    def _serialize_n(self, value):
        number = str(_context.create_decimal(value))
        if number in ['Infinity', 'NaN']:
            raise TypeError('Infinity and NaN not supported')
        return number

    def _serialize_s(self, value):
        return value

    def _serialize_b(self, value):
        if isinstance(value, bytearray) or isinstance(value, bytes):
            value = value.value
        return value

    def _serialize_ss(self, value):
        return [self._serialize_s(s) for s in value]

    def _serialize_ns(self, value):
        return [self._serialize_n(n) for n in value]

    def _serialize_bs(self, value):
        return [self._serialize_b(b) for b in value]

    def _serialize_l(self, value):
        return [self.serialize(v) for v in value]

    def _serialize_m(self, value):
        return dict([(k, self.serialize(v)) for k, v in value.items()])
