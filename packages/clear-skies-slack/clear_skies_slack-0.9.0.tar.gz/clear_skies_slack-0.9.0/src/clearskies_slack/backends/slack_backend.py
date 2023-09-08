import clearskies
import requests
from typing import Dict, Any, List, Callable


class SlackBackend(clearskies.backends.ApiBackend):
    def __init__(self, requests: requests, slack_auth: clearskies.authentication.SecretBearer) -> None:
        super().__init__(requests)
        self.configure(
            url="https://slack.com/api",
            auth=slack_auth,
        )

    def _build_records_request(self, configuration: Dict[str, Any]) -> List[Any]:
        suffix = ""
        url_params = {}
        table_name = configuration["table_name"]
        cursor = configuration.get("pagination").get("cursor")
        limit = configuration.get("limit")
        if cursor:
            url_params["cursor"] = cursor
        if limit:
            url_params["limit"] = limit
        if url_params:
            suffix += "?" + urllib.parse.urlencode(url_params)

        return [f"{self.url}/{table_name}{suffix}", "GET", {}, {}]

    def _map_records_response(self, records: Any) -> List[Dict[str, Any]]:
        # we get here if we hit the list endpoint
        if "channels" in records:
            return records["channels"]
        return records

    def records(
        self,
        configuration: Dict[str, Any],
        model: clearskies.Model,
        next_page_data: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        configuration = self._check_query_configuration(configuration)
        [url, method, json_data, headers] = self._build_records_request(configuration)
        response = self._execute_request(
            url, method, json=json_data, headers=headers, is_retry=False
        )
        json_response = response.json()
        records = self._map_records_response(json_response)
        if type(next_page_data) == dict and json_response.get("response_metadata", {}).get("next_cursor"):
            next_page_data["cursor"] = json_response["response_metadata"]["next_cursor"]
        return records

    def validate_pagination_kwargs(
        self, kwargs: Dict[str, Any], case_mapping: Callable[str, str]
    ) -> str:
        extra_keys = set(kwargs.keys()) - set(self.allowed_pagination_keys())
        if len(extra_keys):
            key_name = case_mapping("cursor")
            return (
                "Invalid pagination key(s): '"
                + "','".join(extra_keys)
                + f"'.  Only '{key_name}' is allowed"
            )
        if "cursor" not in kwargs:
            key_name = case_mapping("cursor")
            return "You must specify 'cursor' when setting pagination"
        return ""

    def allowed_pagination_keys(self) -> List[str]:
        return ["cursor"]
