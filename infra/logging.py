import json
import logging
from datetime import datetime, timezone


def configure():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("pika").setLevel(logging.ERROR)


def log(event, **fields):
    print(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": event,
                      **fields}, ensure_ascii=False), flush=True)
