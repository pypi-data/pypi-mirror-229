# Deep Replacer

Given a list, set, tuple or dictionary as data input, loop through the data and replace all values that are not a list,
set, tuple or dictionary using a replace function.

## How to use

### Basic example

```python
from deep_replacer import DeepReplacer

replacer = DeepReplacer()


def my_replace_func(value: str):
    """Return value to upper case"""

    return value.upper()


data = [
    {
        "name": "John Doe",
        "hobbies": {
            "sport": ["football", "tennis"],
            "music": ["singing", "guitar", "piano"],
        },
    }
]
data_replaced = replacer.replace(data=data, replace_func=my_replace_func)

print(data_replaced)
```

### Output:

```json
[
  {
    "name": "JOHN DOE",
    "hobbies": {
      "sport": [
        "FOOTBALL",
        "TENNIS"
      ],
      "music": [
        "SINGING",
        "GUITAR",
        "PIANO"
      ]
    }
  }
]
```

### Example using `key_depth_rules` argument

```python
from deep_replacer import DeepReplacer
from deep_replacer import key_depth_rules

replacer = DeepReplacer()


def my_replace_func(value: str):
    """Return value to upper case"""

    return value.upper()


data = [
    {
        "name": "John Doe",
        "hobbies": {
            "sport": ["football", "tennis"],
            "music": ["singing", "guitar", "piano"],
        },
    }
]
data_replaced = replacer.replace(
    data=data,
    replace_func=my_replace_func,
    key_depth_rules={"hobbies:sport": [key_depth_rules.IGNORE]},  # Ignore key at depth 'hobbies:sport'
)

print(data_replaced)
```

### Output:

```json
[
  {
    "name": "JOHN DOE",
    "hobbies": {
      "sport": [
        "football",
        "tennis"
      ],
      "music": [
        "SINGING",
        "GUITAR",
        "PIANO"
      ]
    }
  }
]
```