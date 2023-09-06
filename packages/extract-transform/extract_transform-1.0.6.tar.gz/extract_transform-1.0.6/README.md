# 📦 Extract Transform
[![PyPI version](https://badge.fury.io/py/extract-transform.svg)](https://pypi.org/project/extract-transform) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`Extract Transform` is a Python library offering robust tools for encoding, decoding, and transforming intricate Python objects. Designed for efficient nested data manipulation and custom data type handling, it's an indispensable tool for preparing and structuring data, especially in machine learning workflows.

# Installation

Install the library via pip:

```shell
pip install extract-transform
```

or poetry:

```shell
poetry add extract-transform
```

# Usage

`Extract Transform` comprises a variety of extractors, each tailored to handle specific types or transformations. To utilize the library's capabilities, you would typically select the relevant extractor and apply it to your data.

## Basic example

```python
from extract_transform import Record, Transform

extractor = Record({"key": Transform(lambda s: s.upper())})
result = extractor.extract({"key": "value"}) # {"key": "VALUE"}
```

## Advanced Examples

For more intricate use-cases and advanced examples, please refer to the following:

- [Machine learning preprocessing](https://github.com/frederikvanhevel/extract-transform/blob/master/examples/machine_learning_preprocessing.py)
- [OpenWeather API Example](https://github.com/frederikvanhevel/extract-transform/blob/master/examples/openweather_api.py)
- [Twitter API Example](https://github.com/frederikvanhevel/extract-transform/blob/master/examples/twitter_api.py)
- [Experian API Example](https://github.com/frederikvanhevel/extract-transform/blob/master/examples/experian_api.py)


## Available Extractors

- [Basic types](#basic-types)
- [Complex types](#complex-types)
- [Data manipulation](#data-manipulation)
- [Custom extractors](#custom-extractors)

### Basic types

- [Boolean](#boolean)
- [Decimal](#decimal)
- [Float](#float)
- [Integer](#integer)
- [String](#string)
- [Hexadecimal](#hexadecimal)
- [Raw](#raw)

#### Boolean

Converts data to a boolean using provided truthy and falsy values.

**Input:** "true", "false", 1, 0
**Output:** `True` or `False`.

```python
extractor = Boolean()
extractor.extract("true") # Output: True

extractor = Boolean(truthy_values=["yes"], falsy_values=["no"])
extractor.extract("yes") # Output: True
```

---

#### Decimal

Converts data to a decimal with specified precision and scale.

**Input:** "123.456", 123.456, "123", 123, etc.  
**Output:** Rounded decimal.Decimal value.

```python
extractor = Decimal()
extractor.extract("123.456") # Output: decimal.Decimal
```
---

#### Float

Converts data to a float.

**Input:** "123.456", 123.456, "123", 123, etc.  
**Output:** Float value.

```python
extractor = Float()
extractor.extract("123.456") # Output: 123.456
```



---

#### Integer

Converts data to its integer representation.

**Input:** "12345", 12345, "1a3f" (hexadecimal), etc.  
**Output:** Integer value.

```python
extractor = Integer()
extractor.extract("12345") # Output: 12345
```

---

#### String

Converts data to its string representation.

**Input:** 12345, True, [1, 2, 3], etc.  
**Output:** String representation, e.g., "12345".

```python
extractor = String()
extractor.extract(550) # Output: "550"
```

---

#### Hexadecimal

Converts a hexadecimal string to an integer.

**Input:** "1a3f", "fa3c", etc.  
**Output:** Integer representation of the hexadecimal.

```python
extractor = Hexadecimal()
extractor.extract("1a3f") # Output: 6719
```

---

#### Raw

Returns data as-is without processing.

**Input:** 12345, "Hello", {"key": "value"}, etc.  
**Output:** Input data without any alterations.

```python
extractor = Raw()
extractor.extract("12345") # Output: "12345"
```

### Complex types

- [Array](#array)
- [Record](#record)
- [NumericWithCodes](#numericwithcodes)

#### Array

Processes input into a list, transforming each item based on a provided extractor.

**Input:** A list or a single item. E.g., ["Alice", "Bob"] or "Alice".  
**Output:** List with items processed according to the extractor, e.g., ["Alice", "Bob"].

```python
extractor = Array()
extractor.extract(["Alice", "Bob"]) # Output: ["Alice", "Bob"]
```

---

#### Record

Processes a dictionary by transforming values based on provided field mappings.

**Input:** Dictionary with fields like {"name": "Alice", "age": 30}.  
**Output:** New dictionary with mapped fields, e.g., {"name": "Alice", "age": 30}.

```python
extractor = Record({
    ("identity", "id"): Integer(),
    "amount": Integer()
})

extractor.extract({
    "identity": 5,
    "amount": "25"
}) # Output: {"id": 5, "amount": 25}
```
---

#### NumericWithCodes

Extracts numeric values and categorizes them based on boundaries. If the value lies within boundaries, it's returned as-is; otherwise, returned as a string.

**Input:** Numeric representations like 5, 5.0, "5.0", or Decimal('5.0').  
**Output:** Dictionary with 'value' and 'categorical' keys. E.g., {"value": 5, "categorical": None} or {"value": None, "categorical": "15"}.

```python
extractor = NumericWithCodes(
    Integer(),
    min_val=1,
    max_val=100
)

extractor.extract(55) # Output: {"value": 55, "categorical": None}
extractor.extract(9999) # Output: {"value": None, "categorical": "9999"}
```


### Data manipulation

- [Compose](#compose)
- [Count](#count)
- [DefaultValue](#defaultvalue)
- [DictMap](#dictmap)
- [Exists](#exists)
- [Filter](#filter)
- [Flatten](#flatten)
- [MapValue](#mapvalue)
- [Pivot](#pivot)
- [SelectListItem](#selectlistitem)
- [Select](#select)
- [SortDictList](#sortdictlist)
- [Split](#split)
- [Transform](#transform)
- [Union](#union)
- [Unpivot](#unpivot)
- [When](#when)


#### Compose

Chains multiple extractors, passing the output of one as the input to the next.

**Input:** Data compatible with the first extractor, e.g., if the first expects a string, provide a string.  
**Output:** Data processed by all extractors. The nature depends on the sequence, e.g., if the last returns an integer, the output will be an integer.

```python
extractor = Compose(Boolean(), Integer())
extractor.extract("true") # Output: 1
```

---

#### Count

Counts the items in a list based on a given predicate.

**Input:** A list of items.  
**Output:** Integer representing the count of items satisfying the predicate.

```python
extractor = Count()
extractor.extract([1, 2, 3, 4]) # Output: 4

extractor = Count(lambda x: x > 2)
extractor.extract([1, 2, 3, 4]) # Output: 2
```

---

#### DefaultValue

Returns the input if it's not None; otherwise, a default value.

**Input:** Any data type or None.  
**Output:** Input data if it's not None; otherwise, the default value.

```python
extractor = DefaultValue(1000)
extractor.extract(None) # Output: 1000
extractor.extract(550) # Output: 550
```

---

#### DictMap

Processes each dictionary value through a specified extractor, returning the processed dictionary.

**Input:** Dictionary with arbitrary keys and values, e.g., {"name": "Alice", "age": "30"}.  
**Output:** Dictionary with processed values, e.g., with an integer extractor: {"name": "Alice", "age": 30}.

```python
extractor = DictMap(Integer())
extractor.extract({"a": "10", "b": "20"}) # Output: {"a": 10, "b": 20}
```

---

#### Exists

Checks if a specified key exists in the given data.

**Input:** Data that supports the "in" operation, typically dictionaries or lists. E.g., `{"name": "Alice", "age": 30}` or `["Alice", "Bob", "Charlie"]`.  
**Output:** Boolean indicating the key's existence. E.g., for key "name" and dictionary input: `True`.

```python
extractor = Exists("Alice")
extractor.extract(["Alice", "Bob", "Charlie"]) # Output: True
```
---

#### Filter

Filters items in a list based on a predicate.

**Input:** A list of items.  
**Output:** A list of items that satisfy the predicate.

```python
extractor = Filter(lambda x: x > 2)
extractor.extract([1, 2, 3, 4]) # Output: [3, 4]
```

---

#### Flatten

Flattens a nested dictionary into a single-level dictionary with compound keys.

**Input:** A possibly nested dictionary. E.g., `{"a": {"b": 1, "c": {"d": 2}}}`.  
**Output:** A single-level dictionary. E.g., `{"a.b": 1, "a.c.d": 2}`.

```python
extractor = Flatten()
extractor.extract({"a": {"b": 1, "c": {"d": 2}}}) # Output: {"a.b": 1, "a.c.d": 2}
```

---

#### MapValue

Maps input values to a representation based on a provided mapping.

**Input:** A value that might exist in the mapping. E.g., `1` or `"apple"`.  
**Output:** Mapped value or the default. E.g., for mapping `{1: "TypeA", "apple": "fruit"}`:
- Input: `1` -> Output: `"TypeA"`
- Input: `"orange"` -> Output: `"UnknownType"` (if default is "UnknownType").

```python
extractor = MapValue({1: "TypeA", 2: "TypeB", 3: "TypeC"}, default="UknownType")
extractor.extract(1) # Output: "TypeA"
extractor.extract(5) # Output: "UknownType"
```

---

#### Pivot

Groups data items by a specified key and applies a result extractor to each group.

**Input:** A list of dictionaries.  
**Output:** Dictionary with keys as distinct values from the input list's 'key' field, and values as the result of the `result_extractor` applied to items with the same key.

```python
extractor = Pivot("group", Raw(), exclude_key=True)
data = [
    {"group": "A", "value": "10"},
    {"group": "B", "value": "20"},
    {"group": "A", "value": "30"},
]
extractor.extract(data) # Output: {"A": [{"value": "10"}, {"value": "30"}], "B": [{"value": "20"}]
```

---

#### SelectListItem

Retrieves an item from a list by its position or a criteria.

**Input:** A list, like [1, 2, 3, 4].  
**Output:** Item based on position or criteria, e.g., for position 2: 3.

```python
extractor = SelectListItem()
extractor.extract([1, 2, 3]) # Output: 1

extractor = SelectListItem(position=1)
extractor.extract([10, 20, 30]) # Output: 20

extractor = SelectListItem(criteria=lambda x: x > 15)
extractor.extract([10, 20, 30]) # Output: 20
```

---

#### Select

Extracts a value from a dictionary by a key and optionally processes it.

**Input:** A dictionary, like {"name": "Alice", "age": 30}.  
**Output:** Value based on the key and optional extractor, e.g., for key "name": "Alice".

```python
extractor = Select(key="age")
extractor.extract({"name": "John", "age": 25}) # Output: 25
```

---

#### SortDictList

Sorts dictionaries in a list by a specified key.

**Input:** List of dictionaries with consistent keys, like [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}].  
**Output:** Sorted list by `sort_key`, e.g., for `sort_key="age"`: [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}].

```python
data = [
    {"name": "Alice", "age": 28},
    {"name": "Bob", "age": 22},
    {"name": "Charlie", "age": 24},
]

extractor = SortDictList(sort_key="age")

extractor.extract(data)

# Output: [
#     {"name": "Bob", "age": 22},
#     {"name": "Charlie", "age": 24},
#     {"name": "Alice", "age": 28},
# ]
```

---

#### Split

Splits a string by a separator and applies an extractor to the substrings.

**Input:** A string with the separator, like "Apple,Banana,Cherry".  
**Output:** List of extracted values from substrings, e.g., for `sep=","`: ["Apple", "Banana", "Cherry"].


```python
extractor = Split(sep=",")
extractor.extract("apple,banana,grape") # Output: ["apple", "banana", "grape"]
```

#### Transform

Applies a transformation function to the data and optionally processes it with another extractor.

**Input:** Compatible data with the transformation function.  
**Output:** If no extractor is provided, it's the transformed data. If an extractor is given, it's the result of the extractor on the transformed data.  
**Example:** For a function that capitalizes strings and an extractor that reverses the string, input 'apple' gives 'ELPPA'.


```python
extractor = Transform(lambda x: x * 2, Raw())
extarctor.extract(2) # Output: 4
```

---

#### Union

Tries multiple conditions in sequence and returns the result of the first successful one.

**Input:** Data that can be processed by at least one of the given extractors.  
**Output:** Result of the first successful extractor or the default, if provided.

```python
extractor = Union(Raw(), Raw())
extractor.extract("test") # Output: "test"
```

---

#### Unpivot

Converts a dictionary into a list of dictionaries with specific key-value pairs.

**Input:** Dictionary with values as lists.  
**Output:** A list of dictionaries. Each dictionary has two keys: 'category' for the original dictionary's key and 'value' for the extracted value from the original list.

```python
data = {
    "Fruits": ["Apple", "Banana"],
    "Vegetables": ["Carrot", "Broccoli"]
}

extractor = Unpivot(key="category", result_extractor=String())
extractor.extract(data)

# Output: [
#     {"category": "Fruits", "value": "Apple"},
#     {"category": "Fruits", "value": "Banana"},
#     {"category": "Vegetables", "value": "Carrot"},
#     {"category": "Vegetables", "value": "Broccoli"},
# ]
```

---

#### When

Uses an extractor based on a given condition.

**Input:** Any data that the condition function can evaluate.  
**Output:** If the condition is true, the extracted data is returned. Otherwise, it returns None.

```python
extractor = When(lambda x: x == "yes", Raw())
extractor.extract("yes") # Output: yes
extractor.extract("no") # Output: None
```

### Dates and times

- [Date](#date)
- [Datetime](#datetime)
- [DatetimeUnix](#datetimeunix)
- [RelativeDate](#relativedate)
- [RelativeDatetime](#relativedatetime)

#### Date

Extracts a date from its string representation using the specified format.

**Input:** A string that matches the date format (e.g., "2023-05-01" for default "%Y-%m-%d" format).  
**Output:** A date object matching the input (e.g., date(2023, 5, 1)).

```python
extractor = Date()
extractor.extract("2023-05-01") # Output: datetime.date
```

---

#### DateTime

Parses a date-time string into a datetime object. Can adjust for timezones.

**Input:** A date-time string (e.g., "2023-04-30T17:00:00" for the default format).  
**Output:** The parsed datetime object, optionally adjusted to the provided timezone. If there's a parsing error, the output is None.

```python
extractor = DateTime()
extractor.extract("2023-04-30T17:00:00") # Output: datetime.date
```

---

#### DatetimeUnix

Turns a UNIX timestamp into a datetime object.

**Input:** A numeric representation of a UNIX timestamp in seconds (e.g., 1619856000).  
**Output:** The corresponding datetime object (e.g., datetime(2023, 4, 30, 17, 0)).

```python
extractor = DatetimeUnix()
extractor.extract(1609459200) # Output: datetime.datetime
```

---

#### RelativeDate

Determines the days difference between an input date string and a reference date from the context.

**Input:** A date string (e.g., "2023-04-30" for the default format).  
**Output:** A float showing the days difference between the input date and the reference date from the context. If the dates are invalid or not provided, the output is None.

```python
extractor = RelativeDate()
extractor.extract("2023-09-05") # Output: 5
```

---

#### RelativeDatetime

Calculates the seconds difference between an input datetime string and a reference datetime from the context.

**Input:** A datetime string (e.g., "2023-04-30T15:30:00" for the default format).  
**Output:** A float representing the seconds difference between the input and the reference datetime. If the datetimes are invalid or not provided, the output is None.

```python
extractor = RelativeDate()
extractor.extract("2023-09-05T15:30:00") # Output: 4.45
```


### Encoding and categorical

- [Categorical](#categorical)
- [Ordinal](#ordinal)
- [OneHot](#onehot)
- [MultiHot](#multihot)

#### Categorical

Validates input data against a predefined set of categories.

**Input:** A string denoting a category (e.g., "category_A").  
**Output:** The input string, if it's in the set of `valid_categories`. If not, a warning is raised, but the input string is still returned without change.

```python
extractor = Categorical({"apple", "banana", "cherry"})
extractor.extract("apple") # Output: apple
extractor.extract("pineapple") # Output: pineapple

extractor = Categorical({"apple", "banana", "cherry"}, raise_on_warning=True)
extractor.extract("pineapple") # Exception

```

---

#### Ordinal

Transforms categorical data into its ordinal representation based on a defined order or explicit mapping.

**Input:** A string representing a category (e.g., "medium").  
**Output:** An integer that denotes the ordinal position of the input category.  
- If the `ordered_categories` is a list like ["low", "medium", "high"] and the input is "medium", the output is 1.  
- If the `ordered_categories` is a dictionary like {"low": 0, "medium": 5, "high": 10} and the input is "medium", the output is 5.

```python
extractor = Ordinal(["low", "medium", "high"])
extractor.extract(1) # Output: "medium"
```

---

#### OneHot

One-hot encodes the input data according to predefined categories.

**Input:** A string that represents a category (e.g., "category_A").  
**Output:** A dictionary where each key is a category from the `categories` list and the corresponding value is either 1 (if the input matches the category) or 0 (if it doesn't).  
For instance, if `categories` = ["category_A", "category_B", "category_C"] and input is "category_A", the output is: {"category_A": 1, "category_B": 0, "category_C": 0}.

```python
extractor = OneHot(["cat", "dog", "bird"])
extractor.extract("cat") # Output: {"cat": 1, "dog": 0, "bird": 0}
```

---

#### MultiHot

Encodes a list of categories into a multi-hot representation based on a list of predefined categories.

**Input:** A list of strings, where each string represents a category (e.g., ["category_A", "category_B"]).  
**Output:** A list of integers (0 or 1) that indicates the presence or absence of each category in the `categories` list.  
Example: If `categories` = ["category_A", "category_B", "category_C"] and the input list is ["category_A", "category_B"], the output is: [1, 1, 0].

```python
extractor = MultiHot(["cat", "dog", "bird"])
extractor.extract(["cat", "bird"]) # Output: [1, 0, 1]
```

## Custom Extractors

In scenarios where the provided built-in extractors aren't adequate for specific data transformation needs, you can create custom extractors by subclassing the `Extractor` class and implementing the `extract` method.

### Example: Temperature Extractor

Let's consider a situation where you have temperature data in Kelvin and want to extract it in Celsius and Fahrenheit formats. 

Here's how you can create a custom `TemperatureExtractor`:

```python
from extract_transform import Extractor

class Temperature(Extractor):
    """
    Extracts the Kelvin temperature and calculates the temperatures in Celsius and Fahrenheit.
    """

    def extract(self, data: Any):
        kelvin = data["temp"]
        celsius = kelvin - 273.15
        fahrenheit = kelvin * 9 / 5 - 459.67

        return {"celsius": celsius, "fahrenheit": fahrenheit}


Temperature().extract({"temp": 310}) # Output: {"celsius": 36.85, "fahrenheit": 98.33}