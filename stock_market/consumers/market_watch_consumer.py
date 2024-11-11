import json

from channels.generic.websocket import WebsocketConsumer

import pandas as pd
from core.configs import STOCK_DB, STOCK_TOP_500_LIMIT

from core.utils import MongodbInterface, add_index_as_id
from stock_market.serializers import PersonMoneyFlowSerailizer
from stock_market.utils import MAIN_PAPER_TYPE_DICT


class MarketWatchConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data):
        text_data = json.loads(text_data)
        index = text_data.get("index")
        if index is None:
            self.send(text_data=json.dumps({index: []}))

        mongo_client = MongodbInterface(db_name=STOCK_DB, collection_name=index)
        results = mongo_client.collection.find(
            {"paper_type": {"$in": list(MAIN_PAPER_TYPE_DICT.keys())}}, {"_id": 0}
        )
        results = pd.DataFrame(results)

        if results.empty:
            results = results.to_dict(orient="records")
            self.send(text_data=json.dumps({index: results}))

        results = results[~results["symbol"].str.contains(r"\d")]
        results = results.sort_values(by=index, ascending=False)
        results = results.head(STOCK_TOP_500_LIMIT)
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results = results.to_dict(orient="records")

        results = PersonMoneyFlowSerailizer(results, many=True)

        self.send(text_data=json.dumps({index: results.data}))
