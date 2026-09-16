import json

def load_json_records(filepath: str) -> list[dict]:
    with open(filepath, 'r') as f:
        return json.load(f)
