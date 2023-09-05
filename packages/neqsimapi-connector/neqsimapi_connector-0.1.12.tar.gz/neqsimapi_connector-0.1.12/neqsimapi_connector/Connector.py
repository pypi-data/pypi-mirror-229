import asyncio
import json
from urllib.parse import urljoin

import httpx
import requests

from neqsimapi_connector.BearerAuth import BearerAuth


def get_url_NeqSimAPI(use_test: bool = False) -> str:
    """Get base url to NeqSimAPI.

    Args:
        use_test (bool, optional): Set true to get url to test environment. Defaults to False.

    Returns:
        str: Base url to NeqSimAPI.
    """
    if use_test:
        return "https://api-neqsimapi-dev.radix.equinor.com"
    else:
        return "https://neqsimapi.app.radix.equinor.com"


def get_auth_NeqSimAPI() -> BearerAuth:
    """Get authentication object containing bearer token.

    Returns:
        BearerAuth: Authentication object for use with request session.
    """
    tenantID = "3aa4a235-b6e2-48d5-9195-7fcf05b459b0"
    client_id = "dde32392-142b-4933-bd87-ecdd28d7250f"
    scope = ["api://dde32392-142b-4933-bd87-ecdd28d7250f/Calculate.All"]

    return BearerAuth.get_bearer_token_auth(
        tenantID=tenantID, clientID=client_id, scopes=scope
    )


async def send_post_request(client, url, data, semaphore):
    async with semaphore:
        response = await client.post(url=url, json=data)
        return json.loads(response.text)


class Connector:
    """Class for getting data from NeqSimAPI restful api."""

    def __init__(
        self,
        url: str = "",
        auth: BearerAuth = None,
        verifySSL: bool = True,
        timeout: float = 180.0,
    ):
        if url is None or len(url) == 0:
            self.base_url = get_url_NeqSimAPI()
        else:
            self.base_url = url

        if auth is None:
            auth = get_auth_NeqSimAPI()
        elif isinstance(auth, str):
            auth = BearerAuth(str)
        elif isinstance(auth, dict) and "access_result" in auth:
            auth = BearerAuth(auth["access_result"])

        self.auth = auth
        self.verifySSL = verifySSL

        self.session = None
        self.async_client = None

        if timeout is None:
            # Set time out to 3 hours
            timeout = 60*60*3


        self.timeout = timeout

    def get_results(self, calculation_id: str, a_sync: bool = True) -> dict:
        """Get results from async calculation with calculation id.

        Args:
            calculation_id (str): Calculation id. Returned when starting calculation with post or post_async.
            a_sync (bool, optional): Set False to loop internally while waiting for a reply from the calculation. Defaults to True.

        Returns:
            dict: Results when finished or dictionary with status.
        """
        if self.session is None:
            self.init_session()

        url = urljoin(self.base_url, f"results/{calculation_id}")
        res = self.session.get(url, timeout=(9, self.timeout))
        res.raise_for_status()

        if a_sync:
            return res.json()
        else:
            res = res.json()
            while (
                isinstance(res, dict)
                and "status" in res.keys()
                and res["status"] == "working"
            ):
                res = self.get_results(calculation_id=calculation_id)

            if isinstance(res, dict) and "result" in res.keys():
                res = res["result"]

            return res

    def post(self, url: str, data: dict) -> dict:
        """Start calculation and get results or status dict from api.

        Args:
            url (str): Full or partial url to end point.
            data (dict): Data to pass to calculation.

        Returns:
            dict: Result or status dict from end point.
        """
        if self.session is None:
            self.init_session()

        if self.base_url not in url:
            url = urljoin(self.base_url, url)
        res = self.session.post(url, json=data, timeout=(9, self.timeout))

        if res.status_code == 422:
            try:
                d = json.loads(res.text)
                property = d["detail"][0]["loc"][1]
                msg = d["detail"][0]["loc"][1]
            except:
                pass  # Failed failing

            raise ValueError(
                f"Failed getting result input {property} is out of range, {msg}"
            )

        res.raise_for_status()

        return res.json()

    def post_async(self, url: str, data: dict) -> dict:
        """Start async calculation and get status result.
        NB! Results must be gotten with get_results()

        Args:
            url (str): Full or partial url to end point.
            data (dict): Data to pass to calculation.

        Returns:
            dict: Status dict or None if endpoint is not async.
        """
        if self.session is None:
            self.init_session()

        res_json = self.post(url, data)

        if isinstance(res_json, dict) and "id" in res_json.keys():
            return res_json["id"], res_json["status"]

        return None

    async def send_requests(self, url, input_data_list, output):
        if self.async_client is None:
            self.init_async_client()

        if self.base_url not in url:
            url = urljoin(self.base_url, url)

        semaphore = asyncio.Semaphore(16)
        tasks = []
        for d in input_data_list:
            task = asyncio.create_task(
                send_post_request(self.async_client, url, d, semaphore)
            )
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            output.append(response)

    def async_post(self, url: str, inputpoints: list) -> list:
        """
        Make concurrent requests to normal endpoint using this function

        Args:
            url (str): Full or partial url to end point.
            data (list): List of (dict) datapoints.

        Returns:
            list: Calculation output as a list of dictionaries.
        """

        if not isinstance(inputpoints, list):
            try:
                inputpoints = list(inputpoints)
            except ValueError:
                inputpoints = [inputpoints]

        if self.base_url not in url:
            url = urljoin(self.base_url, url)
        output = []
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.send_requests(url, inputpoints, output))
        return output

    def init_session(self):
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.verify = self.verifySSL
        if self.verifySSL is False:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
            )

    def init_async_client(self):
        self.async_client = httpx.AsyncClient(
            auth=self.auth, timeout=httpx.Timeout(9, pool=None, read=self.timeout)
        )
