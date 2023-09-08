import time


def get_span_proper_label_from_provider(endpoint_uri):
    return endpoint_uri.split("//")[-1].replace(".", "__").replace("/", "__")


def get_unix_time():
    return int(time.time() * 1000)


class TxPriority:
    Low = "low"
    Medium = "medium"
    High = "high"
