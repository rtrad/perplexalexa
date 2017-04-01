from flask import Flask
import perplex

app = Flask(__name__)

@app.route('/get_response/<string:sentence>')
def get_response(sentence):
    return perplex.get_response(sentence)

if __name__ == '__main__':
    app.run()