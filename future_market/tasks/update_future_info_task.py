import json
import requests
from celery import shared_task
from datetime import datetime
from core.utils import RedisInterface, task_timing


redis_conn = RedisInterface(db=4)

IS_RUNNING = "is_running"


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
    response = requests.get(url=negotiate_url, params=params, timeout=15)
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
    response = requests.get(url=start_url, params=params, timeout=15)

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
    response = requests.get(url=sse_url, params=params, stream=True, timeout=15)
    print("Connected to events. Waiting for responses...")
    return response.iter_lines()


def update_info():
    negotiation_response = negotiate_connection()
    start_connection(negotiation_response["ConnectionToken"])
    event_stream = connect_to_events(negotiation_response["ConnectionToken"])

    for data in event_stream:
        try:
            data = json.loads(data.decode("utf-8").split("data:")[1])
            data = data.get("M")
            for datum in data:
                key: str = datum.get("M")
                value = datum.get("A")

                if key and value and not key.endswith("DateTime"):
                    value = json.dumps(value[0])
                    redis_conn.client.set(key, value)
                    redis_conn.client.set(name=IS_RUNNING, value=0, ex=60)
                    print("SET: ", key)
        except Exception:
            continue


@task_timing
@shared_task(name="update_future_info_task")
def update_future_info():
    is_running = redis_conn.client.get(name=IS_RUNNING)
    if is_running is None:
        update_info()
