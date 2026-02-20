import json
import os
from pathlib import Path

_DEFS_PATH = Path(os.getcwd()) / "definitions.json"

with open(_DEFS_PATH, "r") as f:
    _defs = json.load(f)["routing"]
    if not _defs:
        raise ValueError("Loading Definitions Failed.")


class Topology:
    # Exchanges
    DIRECT_EXCHANGE: str = _defs.get("direct_exchange", "book.events")
    DEAD_LETTER_EXCHANGE: str = _defs.get("dead_letter_exchange", "book.dlx")

    # Routing Keys
    _keys = _defs.get("keys", {})
    CREATION_KEY: str = _keys.get("created", "book.created")
    BORROWING_KEY: str = _keys.get("borrowed", "book.borrowed")
    RETURNED_KEY: str = _keys.get("returned", "book.returned")

    # Queues
    _queues = _defs.get("queues", {})
    CREATION_QUEUE: str = _queues.get("created", "q.book.created")
    BORROWING_QUEUE: str = _queues.get("borrowed", "q.book.borrowed")
    RETURNED_QUEUE: str = _queues.get("returned", "q.book.returned")
    CREATION_DLQ_QUEUE: str = _queues.get("created_dlq", "q.book.created.dlq")
