import json
import pandas as pd

from channels.generic.websocket import WebsocketConsumer

from core.configs import STOCK_MONGO_DB, MARKET_WATCH_TOP_5_LIMIT
from core.utils import MongodbInterface, add_index_as_id

from stock_market.utils import MAIN_PAPER_TYPE_DICT

from dashboard.utils import STOCK_MARKET_WATCH_INDICES


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

        mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name=index)
        results = pd.DataFrame(
            mongo_conn.collection.find(
                {"paper_type": {"$in": list(MAIN_PAPER_TYPE_DICT.keys())}}, {"_id": 0}
            )
        )
        mongo_conn.client.close()

        if results.empty:
            results = results.to_dict(orient="records")
            self.send(text_data=json.dumps({index: results}))

        results = results[~results["symbol"].str.contains(r"\d")]
        results = results.sort_values(by=index, ascending=False)
        results = results.head(MARKET_WATCH_TOP_5_LIMIT)
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results = results.to_dict(orient="records")

        results = STOCK_MARKET_WATCH_INDICES[index](results, many=True)

        self.send(text_data=json.dumps({index: results.data}))
