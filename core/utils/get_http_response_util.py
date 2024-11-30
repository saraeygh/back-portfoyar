import time
import requests

from colorama import Fore, Style


TSETMC_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "cdn.tsetmc.com",
    "Origin": "https://main.tsetmc.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
}


def get_http_response(
    req_method: str = "GET",
    req_url: str = "",
    req_headers: dict = TSETMC_REQUEST_HEADERS,
    req_json: dict = {},
    req_params: dict = {},
    req_data: dict = {},
    req_verify: bool | None = None,
    timeout: int = 10,
):
    request_dict = {
        "method": req_method,
        "url": req_url,
        "timeout": timeout,
    }

    if req_headers:
        request_dict["headers"] = req_headers

    if req_json:
        request_dict["json"] = req_json

    if req_params:
        request_dict["params"] = req_params

    if req_data:
        request_dict["data"] = req_data

    if req_verify is not None:
        request_dict["verify"] = req_verify

    response = []
    for retry in range(1, 4):

        try:
            response = requests.request(**request_dict)

            if response.status_code == 200:
                return response
            else:
                print(
                    Fore.RED
                    + f"ERROR: Status code {response.status_code}, url: {req_url}"
                    + Style.RESET_ALL
                )

        except Exception as e:
            print(Fore.RED)
            print(e)
            print(Style.RESET_ALL)
        time.sleep(2 * retry)

    return response
