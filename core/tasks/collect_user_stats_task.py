import jdatetime

from core.utils import RedisInterface, MongodbInterface
from core.configs import USER_STATS_REDIS_DB, STATS_MONGO_DB
from colorama import Fore, Style

USER_STATS_MONGO_COLLECTION = "user_stats"
redis_conn = RedisInterface(db=USER_STATS_REDIS_DB)
mongo_conn = MongodbInterface(
    db_name=STATS_MONGO_DB, collection_name=USER_STATS_MONGO_COLLECTION
)


def collect_user_stats():
    keys_count = len(redis_conn.client.keys("*"))

    keys = []
    values = []
    for key in redis_conn.client.scan_iter():
        keys.append(key.decode("utf-8"))
        value = redis_conn.client.get(key)
        value = value.decode("utf-8")
        values.append(value)
    content = dict(zip(keys, values))

    redis_conn.client.flushdb()
    today_date = jdatetime.date.today().strftime("%Y/%m/%d")
    new_stat = {
        "date": today_date,
        "count": keys_count,
        "content": content,
    }

    prev_stats = list(mongo_conn.collection.find({}, {"_id": 0}))
    prev_stats.append(new_stat)
    mongo_conn.insert_docs_into_collection(documents=prev_stats)

    print(Fore.GREEN + f"collect today ({today_date}) user stats" + Style.RESET_ALL)
