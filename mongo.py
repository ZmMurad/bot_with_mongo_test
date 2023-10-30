from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps


class Mongo_DB:
    def __init__(self, user=None, password=None, host="localhost", port=27017):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db = None
        self.collection = None
        if user and password:
            self.url = f"mongodb://{user}:{password}@{host}:{port}"
        else:
            self.url = f"mongodb://{host}:{port}"
        self.client = MongoClient(self.url)

    def set_db_collection(self, db, colection):
        self.db = self.client[db]
        self.collection = self.db[colection]

    def make_aggrigate(self, dt_from, dt_upto, group_type):
        dt_from = datetime.strptime(dt_from, "%Y-%m-%dT%H:%M:%S")
        dt_upto = datetime.strptime(dt_upto, "%Y-%m-%dT%H:%M:%S")
        if group_type == "hour":
            group_format = "%Y-%m-%d %H"
        elif group_type == "day":
            group_format = "%Y-%m-%d"
        elif group_type == "month":
            group_format = "%Y-%m"
        else:
            raise ValueError("Неподдерживаемый тип агрегации")
        pipeline = [
            {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": group_format, "date": "$dt"}},
                    "totalValue": {"$sum": "$value"},
                }
            },
            {"$project": {"_id": 0, "label": "$_id", "totalValue": 1}},
            {"$sort": {"label": 1}},
        ]
        result = list(self.collection.aggregate(pipeline))

        dataset = [entry["totalValue"] for entry in result]
        labels = [entry["label"] for entry in result]

        response = {"dataset": dataset, "labels": labels}

        result_json = dumps(response)
        return result_json


