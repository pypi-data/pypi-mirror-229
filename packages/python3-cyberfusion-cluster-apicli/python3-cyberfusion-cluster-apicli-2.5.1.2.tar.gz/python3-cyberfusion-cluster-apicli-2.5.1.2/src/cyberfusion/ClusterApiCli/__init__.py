"""Helper classes to execute Cluster API calls."""

import datetime
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import certifi
import requests
from cached_property import cached_property
from requests.adapters import HTTPAdapter, Retry

from cyberfusion.Common.Config import CyberfusionConfig

METHOD_GET = "GET"
METHOD_PATCH = "PATCH"
METHOD_PUT = "PUT"
METHOD_POST = "POST"
METHOD_DELETE = "DELETE"


@dataclass
class ClusterApiCallException(Exception):
    """Exception to be raised in case API call failed."""

    body: str
    status_code: int


class ClusterApiHealthException(Exception):
    """Exception to be raised in case API health is not up."""

    pass


class ClusterApiRequest:
    """Prepare API request and call ClusterApiCall."""

    SECTION_CONFIG = "clusterapi"

    KEY_CONFIG_SERVER_URL = "serverurl"
    KEY_CONFIG_USERNAME = "username"
    KEY_CONFIG_API_KEY = "apikey"

    def __init__(
        self, authenticate: bool = True, config_file_path: Optional[str] = None
    ) -> None:
        """Construct API request."""
        self.authenticate = authenticate
        self.config_file_path = config_file_path

        self.server_url = self.config.get(
            self.SECTION_CONFIG, self.KEY_CONFIG_SERVER_URL
        )

        self.data: Optional[Union[dict, str]] = None
        self.params: Optional[Union[dict, str]] = None
        self.content_type_header: Optional[str] = None
        self._token_obj: Optional["ClusterApiToken"] = None

        self.check_health()

    @cached_property
    def config(self) -> CyberfusionConfig:
        """Get config."""
        return CyberfusionConfig(path=self.config_file_path)

    @property
    def username(self) -> str:
        """Get username."""
        return self.config.get(self.SECTION_CONFIG, self.KEY_CONFIG_USERNAME)

    @property
    def api_key(self) -> str:
        """Get API key."""
        return self.config.get(self.SECTION_CONFIG, self.KEY_CONFIG_API_KEY)

    @property
    def token_obj(self) -> Optional["ClusterApiToken"]:
        """Get token object."""
        if not self.authenticate:
            return None

        if (not self._token_obj) or (
            datetime.datetime.utcnow() > self._token_obj.expires_at
        ):
            self._token_obj = ClusterApiToken(
                self.server_url, self.username, self.api_key
            )

        return self._token_obj

    @property
    def token_header(self) -> Optional[str]:
        """Get token header."""
        if not self.token_obj:
            return None

        return self.token_obj.header

    def check_health(self) -> None:
        """Check health and raise exception if needed."""
        health = ClusterApiHealth(self.server_url)

        if health.healthy:
            return

        raise ClusterApiHealthException(health.response["status"])

    def GET(self, path: str, data: Optional[dict] = None) -> None:
        """Set API GET request."""
        self.method = METHOD_GET
        self.path = path
        self.params = data
        self.content_type_header = None  # Use default

    def PATCH(self, path: str, data: dict) -> None:
        """Set API PATCH request."""
        self.method = METHOD_PATCH
        self.path = path
        self.data = json.dumps(data)
        self.content_type_header = ClusterApiCall.CONTENT_TYPE_JSON

    def PUT(self, path: str, data: dict) -> None:
        """Set API PUT request."""
        self.method = METHOD_PUT
        self.path = path
        self.data = json.dumps(data)
        self.content_type_header = ClusterApiCall.CONTENT_TYPE_JSON

    def POST(
        self, path: str, data: dict, params: dict = {}  # noqa: B006
    ) -> None:
        """Set API POST request."""
        self.method = METHOD_POST
        self.path = path
        self.data = json.dumps(data)
        self.params = params
        self.content_type_header = ClusterApiCall.CONTENT_TYPE_JSON

    def DELETE(self, path: str) -> None:
        """Set API DELETE request."""
        self.method = METHOD_DELETE
        self.path = path
        self.data = None
        self.content_type_header = None  # Use default

    def execute(self) -> dict:
        """Handle API request with ClusterApiCall."""
        call = ClusterApiCall(
            method=self.method,
            server_url=self.server_url,
            path=self.path,
            token_header=self.token_header,
            content_type_header=self.content_type_header,
            data=self.data,
            params=self.params,
        )

        call.execute()
        call.check()

        return call.response


class ClusterApiHealth:
    """Retrieve API health."""

    STATUS_UP = "up"

    def __init__(self, server_url: str):
        """Construct API request to get API health."""
        self.server_url = server_url

        self.request()

    def request(self) -> None:
        """Execute API request to get API health."""
        call = ClusterApiCall(
            method=METHOD_GET,
            server_url=self.server_url,
            path="/api/v1/health",
        )

        call.execute()
        call.check()

        self._call = call

    @property
    def response(self) -> dict:
        """Get response."""
        return self._call.response

    @property
    def healthy(self) -> bool:
        """Get if healthy."""
        return self.response["status"] == self.STATUS_UP


class ClusterApiToken:
    """Retrieve API token."""

    def __init__(self, server_url: str, username: str, api_key: str):
        """Construct API request to get authentication data."""
        self.server_url = server_url
        self.username = username
        self.api_key = api_key

        self._access_token_call = self._get_access_token()
        self.expires_at: datetime.datetime = (
            datetime.datetime.utcnow()
            + datetime.timedelta(seconds=self._access_token_call["expires_in"])
        )

    def _get_access_token(self) -> dict:
        """Get access token endpoint result."""
        call = ClusterApiCall(
            method=METHOD_POST,
            server_url=self.server_url,
            path="/api/v1/login/access-token",
            data={"username": self.username, "password": self.api_key},
        )
        call.execute()
        call.check()

        return call.response

    def _get_test_token(self) -> dict:
        """Get test token endpoint result."""
        call = ClusterApiCall(
            method=METHOD_POST,
            server_url=self.server_url,
            path="/api/v1/login/test-token",
            token_header=self.header,
        )
        call.execute()
        call.check()

        return call.response

    @property
    def token(self) -> str:
        """Get access token."""
        return self._access_token_call["access_token"]

    @property
    def type(self) -> str:
        """Get token type."""
        return self._access_token_call["token_type"]

    @property
    def header(self) -> str:
        """Get authentication header."""
        return self.type + " " + self.token

    @property
    def clusters_ids(self) -> List[int]:
        """Get IDs of clusters that this API user has access to."""
        return self._get_test_token()["clusters"]

    @property
    def is_superuser(self) -> bool:
        """Get if API user is superuser."""
        return self._get_test_token()["is_superuser"]

    @property
    def is_provisioning_user(self) -> bool:
        """Get if API user is provisioning user."""
        return self._get_test_token()["is_provisioning_user"]


class ClusterApiCall:
    """Construct, execute and check API call."""

    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_NAME_HEADER = "content-type"

    HTTP_CODE_BAD_REQUEST = 400

    NAME_HEADER_AUTHORIZATION = "Authorization"

    TIMEOUT_REQUEST = 60

    def __init__(
        self,
        method: str,
        server_url: str,
        path: str,
        token_header: Optional[str] = None,
        content_type_header: Optional[str] = None,
        data: Optional[Union[dict, str]] = None,
        params: Optional[Union[dict, str]] = None,
    ) -> None:
        """Set API request attributes."""
        self.method = method
        self.server_url = server_url
        self.path = path
        self.token_header = token_header
        self.content_type_header = content_type_header
        self.data = data
        self.params = params

    @property
    def url(self) -> str:
        """Get request URL."""
        return "".join([self.server_url, self.path])

    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {}

        if self.token_header:
            headers[self.NAME_HEADER_AUTHORIZATION] = self.token_header

        if self.content_type_header:
            headers[self.CONTENT_TYPE_NAME_HEADER] = self.content_type_header

        return headers

    @cached_property
    def session(self) -> requests.sessions.Session:
        """Get requests session."""
        session = requests.Session()

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=10,
                backoff_factor=2.5,
                allowed_methods=None,
                status_forcelist=[502, 503],
            )
        )

        session.mount(self.server_url + "/", adapter)

        return session

    def execute(self) -> None:
        """Execute API request."""
        if self.method == METHOD_GET:
            self.request = self.session.get(
                self.url,
                headers=self.headers,
                params=self.params,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_PATCH:
            self.request = self.session.patch(
                self.url,
                headers=self.headers,
                data=self.data,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_PUT:
            self.request = self.session.put(
                self.url,
                headers=self.headers,
                data=self.data,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_POST:
            self.request = self.session.post(
                self.url,
                headers=self.headers,
                data=self.data,
                params=self.params,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_DELETE:
            self.request = self.session.delete(
                self.url,
                headers=self.headers,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

    def check(self) -> None:
        """Check API request status code and content type."""
        if self.request.status_code < self.HTTP_CODE_BAD_REQUEST:
            if self.request.headers[self.CONTENT_TYPE_NAME_HEADER].startswith(
                self.CONTENT_TYPE_JSON
            ):
                self.response = self.request.json()
            else:
                self.response = self.request.text
        else:
            if self.request.headers[self.CONTENT_TYPE_NAME_HEADER].startswith(
                self.CONTENT_TYPE_JSON
            ):
                raise ClusterApiCallException(
                    self.request.json(), self.request.status_code
                )
            else:
                raise ClusterApiCallException(
                    self.request.text, self.request.status_code
                )
