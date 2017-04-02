from flask import Flask, json, request
import perplex
from random_words import RandomWords

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

@app.route('/haiku')
def get_haiku(seed=None):
    if 'seed' in request.args:
        seed = request.args.get('seed')
    if seed is None:
        seed = RandomWords().random_word()
    output = perplex.get_response(seed, length=5)
    output += ', \n' + perplex.get_response(seed, length=7)
    output += ', \n' + perplex.get_response(seed, length=5)
    return output
    
if __name__ == '__main__':
    app.run()
