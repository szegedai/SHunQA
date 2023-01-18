from elasticsearch import Elasticsearch

def get_highlights(es, text):
    # query top 10 guesses
    body = {
        "query": {
            "match": {
                "document": text
            }
        },
        "highlight": {
            "fields": {
                "document": {}
            }
        }
    }
    s = es.search(index='milqa', body=body)

    result_list = list()
    query_result = ""

    for hit in s['hits']['hits']:
        result_dict = dict()
        # print("context: ", hit["_source"], "\n", "highlight: ", hit["highlight"])
        query_result = "\n".join(hit["highlight"]["document"])
        # for query_results in hit["highlight"]["document"]:
        #     query_result += "\n".join(query_results)
        result_dict[hit["_source"]["document"]] = query_result
        result_list.append(result_dict)
        result_list.append("\n")


es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="/path/to/http_ca.crt",
    basic_auth=("elastic", "facebook"),
    verify_certs=False
)

print(get_highlights(es, "Hol zajlik kereskedelmi célú halászat a Dunán napjainkban?"))
