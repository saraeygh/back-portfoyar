import time
import requests


def get_http_response(
    req_method: str = "GET",
    req_url: str = "",
    req_headers: dict = {},
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
                print(f"ERROR: Status code {response.status_code}, url: {req_url}")

        except Exception as e:
            print(e)
        time.sleep(2 * retry)

    return response
