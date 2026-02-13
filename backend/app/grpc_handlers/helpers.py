from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp


def datetime_to_timestamp(dt: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts
