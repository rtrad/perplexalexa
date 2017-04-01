from flask import Flask, json
import perplex

app = Flask(__name__)

@app.route('/respond/<string:sentence>', methods = ['GET'])
def get_response(sentence):
    return json.dumps(perplex.get_response(sentence))

if __name__ == '__main__':
    app.run(debug=True)