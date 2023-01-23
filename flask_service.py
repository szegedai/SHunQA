from flask import Flask
from elasticsearch import Elasticsearch
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
tokenizer = AutoTokenizer.from_pretrained("ZTamas/hubert-qa-milqa")
model = AutoModelForQuestionAnswering.from_pretrained("ZTamas/hubert-qa-milqa")
qa_pipeline = pipeline(
    "question-answering",
    model=model,
    tokenizer=tokenizer
)


@app.route('/<query>')
def predict_from_question(query):
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
        "http://rgai3.inf.u-szeged.hu:3427/",  # localhostra átírni tesztelésre
        http_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
        verify_certs=False
    )

    s = es.search(index='milqa', body=body)

    # The query only returns the text before the question mark, so we add it here.
    question = query + '?'
    # We use the highest ranked document by the elasticsearch.
    context = s['hits']['hits'][0]["_source"]["document"]
    prediction = qa_pipeline({
        'context': context,
        'question': question
    })

    return_value = {"context": context,
                    "question": question,
                    "answer": prediction['answer'],
                    "start": prediction['start'],
                    "end": prediction['end'],
                    "score": prediction['score']}

    return return_value
