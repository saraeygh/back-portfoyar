import json
from tqdm import tqdm
from domestic_market.models import DomesticProducer
from core.utils import get_http_response


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


def get_producer():
    response = get_http_response(
        req_method="POST", req_url=URL, req_json=PAYLOAD, req_headers=HEADERS
    )

    producer = response.content.decode()
    producer = json.loads(producer)
    producer = producer.get("d")
    producer_list_of_dict = json.loads(producer)

    return producer_list_of_dict


def populate_producer(producers: list):
    producer_bulk_create = []
    producer_bulk_update = []
    for producer in tqdm(producers, desc="Get producers list", ncols=10):
        name = producer.get("name")
        code = producer.get("code")
        try:
            ex_producer = DomesticProducer.objects.get(code=code)
            ex_producer.name = name
            producer_bulk_update.append(ex_producer)
        except DomesticProducer.DoesNotExist:
            new_producer = DomesticProducer(name=name, code=code)
            producer_bulk_create.append(new_producer)
        except Exception as e:
            print(e, "CODE: ", code)

    if producer_bulk_create:
        DomesticProducer.objects.bulk_create(producer_bulk_create)

    if producer_bulk_update:
        DomesticProducer.objects.bulk_update(producer_bulk_update, fields=["name"])


def populate_domestic_market_producer():
    producer_list = get_producer()
    populate_producer(producers=producer_list)
