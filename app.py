from flask import Flask, jsonify
from flask_cors import CORS

from routes.auth_route import auth
from routes.transport_route import transport
from routes.record_route import record
from routes.analysis_route import analysis
from routes.feedback_route import feedback

app = Flask(__name__)
CORS(app)

app.secret_key = "your_secret_key"


# 註冊路由
app.register_blueprint(auth)
app.register_blueprint(transport)
app.register_blueprint(record)
app.register_blueprint(analysis)
app.register_blueprint(feedback)


@app.route("/")
def index():
    return jsonify({
        "status": "success",
        "message": "Carbon footprint API is running"
    })


if __name__ == "__main__":
    app.run(
        port=3000,
        debug=True
    )

