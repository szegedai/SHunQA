from flask import Flask, request, render_template, jsonify, send_file
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


@app.route('/query/<query>')
def predict_from_question(query, size):
    body = {
        "size": size,
        "query": {
            "match": {
                "document": query
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
    contexts = list(s['hits']['hits'])
    return_value = list()
    id = 0

    for context_raw in contexts:
        context = context_raw["_source"]["document"]
        prediction = qa_pipeline({
            'context': context,
            'question': question
        })

        return_value.append({"context": context,
                            "question": question,
                            "answer": prediction['answer'],
                            "start": prediction['start'],
                            "end": prediction['end'],
                            "score": prediction['score'],
                            "id": id})
        id += 1

    return return_value
    
#@app.route('/qa/<query>')
@app.route('/qa/', methods = ['POST', 'GET'])
def predict_from_question_gui():

    if request.method == 'POST':
        query = request.form["query"]
        size = request.form["size"]

        return render_template('index.html', data=predict_from_question(query, size), query=query, size=size)
    
    return render_template('index.html', data=None, query=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
