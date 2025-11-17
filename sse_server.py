from flask import Flask, Response, request
from flask_cors import CORS
from queue import Queue, Empty
import json

app = Flask(__name__)
CORS(app, origins="*")

clients = []

@app.route('/stream')
def stream():
    def event_stream(q):
        while True:
            try:
                data = q.get(timeout=0.5)  # wait for new token
                yield f"data: {data}\n\n"
            except Empty:
                yield "data: \n\n"  # heartbeat to keep connection alive

    q = Queue()
    clients.append(q)
    return Response(event_stream(q), mimetype='text/event-stream')

@app.route('/push', methods=['POST'])
def push():
    data = request.json
    json_data = json.dumps(data)
    for q in clients:
        q.put(json_data)
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, threaded=True)

