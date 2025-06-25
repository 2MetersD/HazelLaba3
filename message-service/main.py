from flask import Flask

app = Flask(__name__)

@app.route('/message', methods=['GET'])
def get_message():
    return "Message service is up"

if __name__ == '__main__':
    app.run(port=8010)
