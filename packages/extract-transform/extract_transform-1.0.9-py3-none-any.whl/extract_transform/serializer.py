import json


def serialize_to_json(data, **kwargs):
    return json.dumps(data, default=str, **kwargs)
