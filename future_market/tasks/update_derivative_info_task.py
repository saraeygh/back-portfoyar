from celery_singleton import Singleton

from datetime import datetime
import json
import requests


from samaneh.celery import app
from core.utils import RedisInterface, MongodbInterface, run_main_task
from core.configs import KEY_WITH_EX_REDIS_DB, FUTURE_MONGO_DB


IS_RUNNING = "derivatives_is_running"


def get_now_timestamp_as_str():
    now_timestamp_str = str(int(datetime.now().timestamp()))
    return now_timestamp_str


def negotiate_connection():
    negotiate_url = "https://cdn.ime.co.ir/realTimeServer/negotiate"
    params = {
        "clientProtocol": "2.1",
        "connectionData": '[{"name":"marketshub"}]',
        "_": get_now_timestamp_as_str(),
    }
    response = requests.get(url=negotiate_url, params=params, timeout=59)
    print("Negotiation completed!")
    return response.json()


def start_connection(connection_token):
    start_url = "https://cdn.ime.co.ir/realTimeServer/start"
    params = {
        "transport": "serverSentEvents",
        "clientProtocol": "2.1",
        "connectionToken": connection_token,
        "connectionData": '[{"name":"marketshub"}]',
        "_": get_now_timestamp_as_str(),
    }
    response = requests.get(url=start_url, params=params, timeout=59)

    print("Got connectionToken!")
    return response.text


def connect_to_events(connection_token):
    sse_url = "https://cdn.ime.co.ir/realTimeServer/connect"
    params = {
        "transport": "serverSentEvents",
        "clientProtocol": "2.1",
        "connectionToken": connection_token,
        "connectionData": '[{"name":"marketshub"}]',
        "tid": "0",
    }
    response = requests.get(url=sse_url, params=params, stream=True, timeout=59)
    print("Waiting for event responses...")
    return response.iter_lines()


def update_info():
    negotiation_response = negotiate_connection()
    start_connection(negotiation_response["ConnectionToken"])
    event_stream = connect_to_events(negotiation_response["ConnectionToken"])

    redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)
    mongo_conn = MongodbInterface(db_name=FUTURE_MONGO_DB)
    for data in event_stream:
        redis_conn.client.set(name=IS_RUNNING, value=0, ex=60)
        try:
            data = json.loads(data.decode("utf-8").split("data:")[1])
            data = data.get("M", [])
            for datum in data:
                data_key: str = datum.get("M")
                data_list = datum.get("A")

                if data_key and data_list and not data_key.endswith("DateTime"):
                    mongo_conn.collection = mongo_conn.db[data_key]
                    if isinstance(data_list[0], list):
                        data_list = data_list[0]
                    elif isinstance(data_list[0], dict):
                        data_list = data_list
                    else:
                        data_list = None

                    if data_list:
                        mongo_conn.insert_docs_into_collection(data_list)

                    print(f"New event ->> SET: {data_key}")
        except (json.decoder.JSONDecodeError, IndexError):
            continue
        except Exception as e:
            print(f"{e}")
            raise e


def update_derivative_info_main():
    redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)
    is_running = redis_conn.client.get(name=IS_RUNNING)

    if is_running is None:
        update_info()


@app.task(base=Singleton, name="update_derivative_info_task", expires=60)
def update_derivative_info():

    run_main_task(
        main_task=update_derivative_info_main,
    )
