from flask import Flask
from elasticsearch import Elasticsearch


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/<query>')
def hello(query):
    body = {
        "query": {
            "match": {
                "document": query
            }
        },
        "highlight": {
            "fields": {
                "document": {}
            }
        }
    }

    es = Elasticsearch(
        "http://rgai3.inf.u-szeged.hu:3427/",
        basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
        verify_certs=False
    )

    s = es.search(index='milqa', body=body)

    result_list = list()

    for hit in s['hits']['hits']:
        result_dict = dict()
        # print("context: ", hit["_source"], "\n", "highlight: ", hit["highlight"])
        query_result = " ------- ".join(hit["highlight"]["document"])
        result_dict[hit["_source"]["document"]] = query_result
        result_list.append(result_dict)

    return result_list
