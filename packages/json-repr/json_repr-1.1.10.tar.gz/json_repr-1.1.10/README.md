# json-repr

Pretty print JSON like data structures with a "repr(...)" fallback, e.g. for MongoDB types

## Usage

```python
import json_repr

# JSON: Legacy Mongo Shell Format
original_source = """{
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "persons": [
        {
            "name": "Alice",
            "id": NumberInt(1)
        },
        {
            "name": "Bob",
            "id": NumberInt(2)
        }
    ]
}"""

document = json_repr.eval_mongo_db_json(original_source)

print(document["persons"][0])

dumped_source = json_repr.dumps(document)
print(dumped_source)

print(dumped_source == original_source)
```

## MongoDB

Currently supported (legacy) mongo shell types:

* ObjectId
* NumberInt
* NumberLong
* NumberDecimal
