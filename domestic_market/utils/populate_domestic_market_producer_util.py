import json
from tqdm import tqdm
from domestic_market.models import DomesticProducer
from core.utils import get_http_response


def get_existing_producer():
    existing_producer = DomesticProducer.objects.all().values(
        "id",
        "name",
        "code",
    )

    existing_producer_dict = {}
    for producer in existing_producer:
        existing_producer_dict[
            (
                producer.get("name"),
                producer.get("code"),
            )
        ] = producer.get("id")

    return existing_producer_dict


def get_producer():
    HEADERS = {
        "Host": "www.ime.co.ir",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Length": "12",
        "Origin": "https://www.ime.co.ir",
        "Connection": "keep-alive",
        "Referer": "https://www.ime.co.ir/offer-stat.html",
        "Cookie": "ASP.NET_SessionId=zebwrt1sbsuvpw30ze4wgub3; SiteBikeLoadBanacer=9609d25e7d6e5b16cafdd45c3cf1d1ebdb204366ac7135985c4cd71dffa8dd38",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    PAYLOAD = {"Language": 8}
    URL = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetProducers"

    response = get_http_response(
        req_method="POST", req_url=URL, req_json=PAYLOAD, req_headers=HEADERS
    )

    try:
        producer = response.content.decode()
        producer = json.loads(producer)
        producer = producer.get("d")
        producer_list_of_dict = json.loads(producer)
    except Exception:
        return []

    return producer_list_of_dict


def populate_producer(producers: list):
    existing_producer_dict = get_existing_producer()

    producer_bulk_list = []
    for producer in tqdm(producers, desc="Get producers list", ncols=10):
        name = producer.get("name")
        code = producer.get("code")
        if (name, code) not in existing_producer_dict:
            new_producer = DomesticProducer(name=name, code=code)
            producer_bulk_list.append(new_producer)

    if producer_bulk_list:
        created_producer = DomesticProducer.objects.bulk_create(producer_bulk_list)
    else:
        created_producer = []

    if created_producer:
        for producer in created_producer:
            existing_producer_dict[(producer.name, producer.code)] = producer.id

    return existing_producer_dict


def populate_domestic_market_producer():
    producer_list = get_producer()
    populate_producer(producers=producer_list)
