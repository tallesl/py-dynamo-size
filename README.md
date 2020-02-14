# dynamo-size

[![](https://badge.fury.io/py/dynamo-size.svg)](https://pypi.org/project/dynamo-size)

Roughly calculates [DynamoDB item size](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/CapacityUnitCalculations.html).

```py
item = {
    'Id': 123,
    'Names': [
        'foo',
        'bar',
        'qux',
        # 500 more names
    ]
}

from dynamo_size import calculate_bytes, calculate_kbytes

calculate_bytes(item)  # returns 2025
calculate_kbytes(item)  # return 1.9775390625 (2025 / 1024)
```
