from flask import Flask, json, request
import perplex

app = Flask(__name__)

@app.route('/respond/<string:sentence>', methods = ['GET'])
def get_response(sentence, length=8):
    if 'length' in request.args:
        length = int(request.args.get('length').strip())
    return json.dumps(perplex.get_response(sentence, length=length))

if __name__ == '__main__':
    app.run(debug=True)