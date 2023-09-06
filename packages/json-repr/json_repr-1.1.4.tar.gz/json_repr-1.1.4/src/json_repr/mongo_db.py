import json


def mongo_db_types():
    class MongoDbType:
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return f"{self.__class__.__name__}({json.dumps(self.value, ensure_ascii=False)})"

    global ObjectId

    class ObjectId(MongoDbType):
        pass

    global NumberInt

    class NumberInt(MongoDbType):
        pass

    global null
    null = None

    global true
    true = True

    global false
    false = False
