import json
import requests
from celery import shared_task
from sseclient import SSEClient

from core.utils import RedisInterface, task_timing


def get_sse_client(url):
    try:
        response = requests.get(url=url, stream=True, timeout=15)
        sse_client = SSEClient(response)
        return sse_client
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


redis_conn = RedisInterface(db=4)

IS_RUNNING = "is_running"


def update_info():
    future_url = "https://cdn.ime.co.ir/realTimeServer/connect?transport=serverSentEvents&clientProtocol=2.1&connectionToken=eMAgZA0VboW%2BtM37dNBLC30gqC7gCpFwiBusP59DvcBuJRtlVSYZk1GKPwrOQ0sLTDZpg%2BYXXLG%2FVE5IzYkS3sOsO2pMyFac568ShGXpjquScJyjmyxU1DR5cDdbRNXD&connectionData=%5B%7B%22name%22%3A%22marketshub%22%7D%5D&tid=0"
    sse_client = get_sse_client(future_url)

    if sse_client:
        for event in sse_client.events():
            try:
                data = json.loads(event.data)
                data = data.get("M")
                for datum in data:
                    key: str = datum.get("M")
                    value = datum.get("A")

                    if key and value and key.endswith("Info"):
                        value = json.dumps(value)
                        redis_conn.client.set(key, value)
                        redis_conn.client.set(name=IS_RUNNING, value=0, ex=60 * 5)
            except Exception as e:
                print(e)
                continue
    else:
        print("Failed to establish SSE connection.")


@task_timing
@shared_task(name="update_future_info_task")
def update_future_info():
    is_running = redis_conn.client.get(name=IS_RUNNING)
    if is_running is None:
        update_info()
