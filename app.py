from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
import requests
import os
from bson import ObjectId
from dotenv import load_dotenv

# Load non-sensitive environment variables
load_dotenv()

app = Flask(__name__, static_folder='public')

mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/prompts')
client = MongoClient(mongo_url)
db = client.get_default_database()

prompts_col = db.prompts

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    okta_domain = os.getenv('OKTA_DOMAIN')
    if not okta_domain:
        return jsonify({'error': 'OKTA_DOMAIN not configured'}), 500
    try:
        resp = requests.post(
            f"{okta_domain}/api/v1/authn",
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'}
        )
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException:
        return jsonify({'error': 'Authentication failed'}), 401

@app.route('/prompts', methods=['GET'])
def get_prompts():
    prompts = []
    for p in prompts_col.find():
        p['_id'] = str(p['_id'])
        prompts.append(p)
    return jsonify(prompts)

@app.route('/prompts', methods=['POST'])
def create_prompt():
    prompt = request.get_json()
    prompt.setdefault('likes', 0)
    prompt.setdefault('comments', [])
    result = prompts_col.insert_one(prompt)
    prompt['_id'] = str(result.inserted_id)
    return jsonify(prompt)

@app.route('/prompts/<pid>/like', methods=['POST'])
def like_prompt(pid):
    result = prompts_col.find_one_and_update(
        {'_id': ObjectId(pid)},
        {'$inc': {'likes': 1}},
        return_document=True
    )
    if not result:
        return '', 404
    return jsonify({'likes': result['likes']})

@app.route('/prompts/<pid>/comments', methods=['POST'])
def add_comment(pid):
    comment = request.get_json()
    comment.setdefault('createdAt', None)
    result = prompts_col.find_one_and_update(
        {'_id': ObjectId(pid)},
        {'$push': {'comments': comment}},
        return_document=True
    )
    if not result:
        return '', 404
    return jsonify(result['comments'])

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 3000)))
