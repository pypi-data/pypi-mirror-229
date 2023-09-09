import clearskies
from clearskies.column_types import string
from collections import OrderedDict
from typing import Any, Dict


class Message(clearskies.Model):
    def __init__(self, message_backend, columns):
        super().__init__(message_backend, columns)

    id_column_name = "ts"

    @classmethod
    def table_name(cls) -> str:
        return "chat"

    def columns_configuration(self) -> Dict[str, Any]:
        return OrderedDict(
            [
                string("ts"),
                string("channel"),
                string("thread_ts"),
                string("text"),
            ]
        )
