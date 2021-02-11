from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

access_key = "AKIAZELJK6BJF5234HAC"

@app.route("/")
def hello():
    return "Hello World!"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)