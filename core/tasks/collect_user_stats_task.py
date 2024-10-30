from celery import shared_task
import jdatetime

from core.utils import RedisInterface, MongodbInterface, task_timing
from core.configs import USER_STATS_REDIS_DB, STATS_MONGO_DB

USER_STATS_MONGO_COLLECTION = "user_stats"
redis_conn = RedisInterface(db=USER_STATS_REDIS_DB)
mongo_conn = MongodbInterface(
    db_name=STATS_MONGO_DB, collection_name=USER_STATS_MONGO_COLLECTION
)


@task_timing
@shared_task(name="collect_user_stats_task")
def collect_user_stats():
    keys_count = len(redis_conn.client.keys("*"))
    redis_conn.client.flushdb()
    new_stat = {
        "date": jdatetime.date.today().strftime("%Y/%m/%d"),
        "count": keys_count,
    }

    prev_stats = list(mongo_conn.collection.find({}, {"_id": 0}))
    prev_stats.append(new_stat)
    mongo_conn.insert_docs_into_collection(documents=prev_stats)
