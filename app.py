from flask import Flask, render_template, request
from question_match import GraphQA
import json

graph_qa = GraphQA()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    answer = graph_qa.query(data['question'])
    return json.dumps({'answer': answer}, ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True)