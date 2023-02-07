from flask import Flask, request, render_template, jsonify, send_file
from elasticsearch import Elasticsearch
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import spacy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
tokenizer = AutoTokenizer.from_pretrained("ZTamas/hubert-qa-milqa")
model = AutoModelForQuestionAnswering.from_pretrained("ZTamas/hubert-qa-milqa")
qa_pipeline = pipeline(
    "question-answering",
    model=model,
    tokenizer=tokenizer
)

nlp_hu = spacy.load("hu_core_news_trf")

@app.route('/query/<query>')
def predict_from_question(query, size):
    doc_q = nlp_hu(query)
    clean_tokens = list()

    for token in doc_q:
        # print(token.text, token.pos_, token.dep_)
        if token.pos_ not in ['DET', 'ADV', 'PRON', 'PUNCT']:
            clean_tokens.append(token.lemma_)

    clean_question = " ".join(clean_tokens)

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

    s = es.search(index='milqa_w_lemma_w_offical_context', body=body)


    # The query only returns the text before the question mark, so we add it here.
    official_question = query if query[-1:] == '?' else query + '?'
    # We use the highest ranked document by the elasticsearch.
    contexts = list(s['hits']['hits'])
    return_value = list()
    id = 0

    for context_raw in contexts:
        lemmatized_context = context_raw["_source"]["document"]
        official_context = context_raw["_source"]["offical_document"]
        elastic_score = context_raw["_score"]
        prediction = qa_pipeline({
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
