from flask import Flask, request, render_template, jsonify, send_file
from elasticsearch import Elasticsearch
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import spacy
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

with open('config.json', 'r') as config:
    config_variables = json.load(config)

question_answering_hubert = config_variables["hubert_qa_pipeline"][2]["pipeline"]
tokenizer_hubert = AutoTokenizer.from_pretrained(config_variables["hubert_qa_pipeline"][0]["tokenizer"])
model_hubert = AutoModelForQuestionAnswering.from_pretrained(config_variables["hubert_qa_pipeline"][1]["model"])

qa_pipeline_hubert = pipeline(question_answering_hubert,
                              model=model_hubert,
                              tokenizer=tokenizer_hubert)

question_answering_roberta = config_variables["roberta_qa_pipeline"][0]["pipeline"]
tokenizer_roberta = config_variables["roberta_qa_pipeline"][1]["tokenizer"]
model_roberta = config_variables["roberta_qa_pipeline"][2]["model"]
device_roberta = int(config_variables["roberta_qa_pipeline"][3]["device"])
handle_impossible_answer_roberta = bool(config_variables["roberta_qa_pipeline"][4]["handle_impossible_answer"])
max_answer_len_roberta = int(config_variables["roberta_qa_pipeline"][5]["max_answer_len"])

qa_pipeline_roberta = pipeline(question_answering_roberta,
                               tokenizer=tokenizer_roberta,
                               model=model_roberta,
                               device=device_roberta,
                               handle_impossible_answer=handle_impossible_answer_roberta,
                               max_answer_len=max_answer_len_roberta)


nlp_hu = spacy.load("hu_core_news_trf")

@app.route('/query/<query>')
def predict_from_question(query, size, elastic, model_type):
    doc_q = nlp_hu(query)
    clean_tokens = list()

    for token in doc_q:
        # print(token.text, token.pos_, token.dep_)
        if token.pos_ not in ['DET', 'ADV', 'PRON', 'PUNCT']:
            clean_tokens.append(token.lemma_)

    clean_question = " ".join(clean_tokens)

    prediction = dict()

    body = {
        "size": size,
        "query": {
            "match": {
                "document": clean_question
            }
        }
    }

    es = Elasticsearch(
        "http://rgai3.inf.u-szeged.hu:3427/",  # localhostra átírni tesztelésre
        http_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
        verify_certs=False
    )

    s = es.search(index=elastic, body=body)

    # The query only returns the text before the question mark, so we add it here.
    official_question = query if query[-1:] == '?' else query + '?'
    # We use the highest ranked document by the elasticsearch.
    contexts = list(s['hits']['hits'])
    return_value = list()
    id = 0

    for context_raw in contexts:
        lemmatized_context = context_raw["_source"]["document"]
        official_context = context_raw["_source"]["official_document"]
        elastic_score = context_raw["_score"]

        if model_type == "hubert":
            prediction = qa_pipeline_hubert({
                'context': official_context,
                'question': official_question
            })
        elif model_type == "xlm-roberta-large":
            prediction = qa_pipeline_roberta({
                'context': official_context,
                'question': official_question
            })

        return_value.append({"lemmatized_context": lemmatized_context,
                             "official_question": official_question,
                             "official_context": official_context,
                             "answer": prediction['answer'],
                             "start": prediction['start'],
                             "end": prediction['end'],
                             "model_score": prediction['score'],
                             "elastic_score": elastic_score,
                             "id": id})
        id += 1

    return return_value


# @app.route('/qa/<query>')
@app.route('/qa/', methods=['GET', 'POST'])
def predict_from_question_gui():
    if request.method == 'POST':
        query = request.form["query"]
        size = request.form["size"]
        elastic = request.form["elastic"]
        model_type = request.form["model_type"]

        return render_template('index.html',
                               data=predict_from_question(query, size, elastic, model_type),
                               query=query,
                               size=size,
                               elastic=elastic,
                               model_type=model_type)

    return render_template('index.html',
                           data=None,
                           query=None)


@app.route('/qa/api/', methods=['GET', 'POST'])
def rest_api():
    record = json.loads(request.data)
    query = predict_from_question(record["query"], record["size"], record["elastic"], record["model_type"])

    with open("./web_service/result.json", "w") as result:
        result.write(json.dumps(query, indent=4))

    return jsonify(query)

# curl -X POST https://chatbot-rgai3.inf.u-szeged.hu/qa/api/ -H 'Content-Type: application/json' -d @./web_service/data.json


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
