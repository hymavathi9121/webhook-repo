from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__)
CORS(app)

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['webhook_db']
collection = db['events']

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')

    data = {
        'author': payload['sender']['login'],
        'timestamp': datetime.utcnow(),
        'action_type': event_type,
        'from_branch': '',
        'to_branch': '',
    }

    if event_type == 'push':
        data['to_branch'] = payload['ref'].split('/')[-1]

    elif event_type == 'pull_request':
        data['from_branch'] = payload['pull_request']['head']['ref']
        data['to_branch'] = payload['pull_request']['base']['ref']

    elif event_type == 'merge':
        # Optional - bonus if implemented
        data['from_branch'] = payload['pull_request']['head']['ref']
        data['to_branch'] = payload['pull_request']['base']['ref']

    collection.insert_one(data)
    return jsonify({"status": "received"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort('timestamp', -1).limit(10))
    formatted = []

    for e in events:
        timestamp = e['timestamp'].strftime("%-d %B %Y - %-I:%M %p UTC")
        if e['action_type'] == 'push':
            formatted.append(f'"{e["author"]}" pushed to "{e["to_branch"]}" on {timestamp}')
        elif e['action_type'] == 'pull_request':
            formatted.append(f'"{e["author"]}" submitted a pull request from "{e["from_branch"]}" to "{e["to_branch"]}" on {timestamp}')
        elif e['action_type'] == 'merge':
            formatted.append(f'"{e["author"]}" merged branch "{e["from_branch"]}" to "{e["to_branch"]}" on {timestamp}')
    
    return jsonify(formatted)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
