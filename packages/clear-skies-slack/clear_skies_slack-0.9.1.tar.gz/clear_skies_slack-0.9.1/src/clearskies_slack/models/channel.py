import clearskies
from clearskies.column_types import string
from collections import OrderedDict
from typing import Any, Dict


class Channel(clearskies.Model):
    def __init__(self, slack_backend, columns):
        super().__init__(slack_backend, columns)

    @classmethod
    def table_name(cls) -> str:
        return "conversations"

    def columns_configuration(self) -> Dict[str, Any]:
        return OrderedDict(
            [
                string("id"),
                string("name"),
            ]
        )
