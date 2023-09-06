import json

# https://www.mongodb.com/docs/mongodb-shell/reference/compatibility/


class MongoDbType:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({json.dumps(self.value, ensure_ascii=False)})"
        )


class ObjectId(MongoDbType):
    pass


class NumberInt(MongoDbType):
    pass


class NumberLong(MongoDbType):
    pass


class NumberDecimal(MongoDbType):
    pass


def eval_mongo_db_json(source):
    return eval(
        source,
        {
            ObjectId.__name__: ObjectId,
            NumberInt.__name__: NumberInt,
            NumberLong.__name__: NumberLong,
            NumberDecimal.__name__: NumberDecimal,
            "null": None,
            "true": True,
            "false": False,
        },
    )
