#!/usr/bin/env python
# encoding: utf-8
import json
import requests

# with code
with open("web_service/data.json", "r") as f:
    data = json.load(f)
headers = {"Content-Type": "application/json"}
url = "http://localhost:5000/api/qa"

json_result = requests.post(url=url,
                            headers=headers,
                            json=data).text

print(json.loads(json_result))

# with curl (CLI)
# curl -X POST localhost:5000/api/qa/ -H 'Content-Type: application/json' -d @./web_service/data.json
