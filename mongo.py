from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
from bson.json_util import dumps
from dateutil.relativedelta import relativedelta

MONTH = "month"
DAY = "day"
HOUR = "hour"


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

    def items_from_db(self, dt_from: datetime, dt_upto: datetime):
        dt_filter = {"dt": {"$gte": dt_from, "$lte": dt_upto}}
        return self.collection.find(dt_filter).sort("dt", ASCENDING)

    def set_db_collection(self, db, colection):
        self.db = self.client[db]
        self.collection = self.db[colection]

    def make_aggrigate(self, dt_from, dt_upto, group_type):
        dt_from: datetime = datetime.fromisoformat(dt_from)
        dt_upto: datetime = datetime.fromisoformat(dt_upto)
        items = self.items_from_db(dt_from, dt_upto)
        res = {"dataset": [], "labels": []}
        current_date = dt_from
        while current_date <= dt_upto:
            res["labels"].append(datetime.isoformat(current_date))
            res["dataset"].append(0)
            if group_type == MONTH:
                current_date += relativedelta(months=1)
            if group_type == DAY:
                current_date += timedelta(days=1)
            if group_type == HOUR:
                current_date += timedelta(hours=1)
        res["labels"].append("9999-09-01T00:00:00")
        res_index = 0
        for item in items:
            date: datetime = item['dt']
            value: int = item['value']
            start_period = datetime.fromisoformat(res['labels'][res_index])
            end_period = datetime.fromisoformat(res['labels'][res_index + 1])
            while not (start_period <= date < end_period):
                res_index += 1
                start_period = datetime.fromisoformat(res['labels'][res_index])
                end_period = datetime.fromisoformat(res['labels'][res_index + 1])
            res['dataset'][res_index] += value
        res['labels'].pop()
        return res

        # if group_type == "hour":
        #     group_format = "%Y-%m-%d %H"
        # elif group_type == "day":
        #     group_format = "%Y-%m-%d"
        # elif group_type == "month":
        #     group_format = "%Y-%m"
        # else:
        #     raise ValueError("Неподдерживаемый тип агрегации")
        # pipeline = [
        #     {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
        #     {
        #         "$group": {
        #             "_id": {"$dateToString": {"format": group_format, "date": "$dt"}},
        #             "totalValue": {"$sum": "$value"},
        #         }
        #     },
        #     {"$project": {"_id": 0, "label": "$_id", "totalValue": 1}},
        #     {"$sort": {"label": 1}},
        #     {
        #         "$group": {
        #             "_id": None,
        #             "dataset": {"$push": "$totalValue"},
        #             "labels": {"$push": "$label"},
        #         }
        #     },
        # ]
        # result = list(self.collection.aggregate(pipeline))
        # print(result)
        # if result:
        #     result = result[0]  # Первый и единственный элемент списка

        # response = {
        #     "dataset": result.get("dataset", []),
        #     "labels": result.get("labels", []),
        # }
        # # dataset = [entry["totalValue"] for entry in result]
        # # labels = [
        # #     datetime.strptime(entry["label"], group_format).strftime(
        # #         "%Y-%m-%dT%H:%M:%S"
        # #     )
        # #     for entry in result
        # # ]
        # # print(dataset)
        # # response = {"dataset": dataset, "labels": labels}

        # result_json = dumps(response)
        # return result_json
