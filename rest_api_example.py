#!/usr/bin/env python
# encoding: utf-8
import json
import requests

# with code
with open("rest_api_example_files/data.json", "r") as f:
    data = json.load(f)
headers = {"Content-Type": "application/json"}
url = "https://chatbot-rgai3.inf.u-szeged.hu/qa/api/"
# url = "http://localhost:5000/qa/api"

json_result = requests.post(url=url,
                            headers=headers,
                            json=data).text

print(json.loads(json_result))

# with curl (CLI)
# curl -X POST https://chatbot-rgai3.inf.u-szeged.hu/qa/api/ -H 'Content-Type: application/json' -d @./rest_api_example_files/data.json
