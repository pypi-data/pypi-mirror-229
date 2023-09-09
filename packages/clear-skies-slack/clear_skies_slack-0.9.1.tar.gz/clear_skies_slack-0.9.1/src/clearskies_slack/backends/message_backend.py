import clearskies
import requests
from typing import Dict, Any, List, Callable
import urllib
from .slack_backend import SlackBackend


class MessageBackend(SlackBackend):
    def _map_records_response(self, records: Any) -> List[Dict[str, Any]]:
        if "messages" in records:
            return records["messages"]
        return records

    def _build_create_request(self, data, model):
        table_name = model.table_name()
        return [f'{self.url}/{table_name}.postMessage', "POST", data, {}]

    def _map_create_response(self, response):
        return response
