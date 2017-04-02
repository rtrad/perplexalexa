from flask import Flask, json, request
import perplex

app = Flask(__name__)

@app.route('/')
def index():
    return 'try going to /respond/<your sentence here> to get a rhyming sentence'

@app.route('/respond/<string:sentence>', methods = ['GET'])
def get_response(sentence):
    if 'length' in request.args:
        length = int(request.args.get('length').strip())
    else:
        length=None
    if 'start_word' in request.args:
        start_word = request.args.get('start_word').strip()
    else:
        start_word = None
    return perplex.get_response(sentence, length=length, start_word=start_word)

if __name__ == '__main__':
    app.run()
