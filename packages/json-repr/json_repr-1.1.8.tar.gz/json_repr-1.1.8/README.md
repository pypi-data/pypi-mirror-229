# json-repr

Pretty print JSON like data structures with a "repr(...)" fallback, e.g. for MongoDB types

## Usage

```python
import json_repr

source = """{
    "_id" : ObjectId("507f1f77bcf86cd799439011"),
	"persons": [
		{
			"name": "Alice"
			"id": NumberInt(1)
		},
		{
			"name": "Bob"
			"id": NumberInt(2)
		}
	]
}"""

persons = json_repr.eval_mongo_db_json(source)

print(persons)

print()

print(json_repr.dumps(persons))
```
