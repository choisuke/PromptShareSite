from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
import requests
import os
from bson import ObjectId

app = Flask(__name__, static_folder='public')

mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/prompts')
client = MongoClient(mongo_url)
db = client.get_default_database()

prompts_col = db.prompts

@app.route('/')
def root_page():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/prompts')
def list_page():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/post')
def post_page():
    return send_from_directory(app.static_folder, 'post.html')

@app.route('/api/login', methods=['POST'])
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

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    prompts = []
    for p in prompts_col.find():
        p['_id'] = str(p['_id'])
        prompts.append(p)
    return jsonify(prompts)

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    prompt = request.get_json()
    prompt.setdefault('likes', 0)
    prompt.setdefault('comments', [])
    prompt.setdefault('createdAt', None)
    result = prompts_col.insert_one(prompt)
    prompt['_id'] = str(result.inserted_id)
    return jsonify(prompt)

@app.route('/api/prompts/<pid>/like', methods=['POST'])
def like_prompt(pid):
    result = prompts_col.find_one_and_update(
        {'_id': ObjectId(pid)},
        {'$inc': {'likes': 1}},
        return_document=True
    )
    if not result:
        return '', 404
    return jsonify({'likes': result['likes']})

@app.route('/api/prompts/<pid>', methods=['DELETE'])
def delete_prompt(pid):
    result = prompts_col.delete_one({'_id': ObjectId(pid)})
    if result.deleted_count:
        return '', 204
    return '', 404

@app.route('/api/prompts/<pid>/comments', methods=['POST'])
def add_comment(pid):
    comment = request.get_json()
    comment.setdefault('_id', str(ObjectId()))
    comment.setdefault('createdAt', None)
    result = prompts_col.find_one_and_update(
        {'_id': ObjectId(pid)},
        {'$push': {'comments': comment}},
        return_document=True
    )
    if not result:
        return '', 404
    return jsonify(result['comments'])

@app.route('/api/prompts/<pid>/comments/<cid>', methods=['DELETE'])
def delete_comment(pid, cid):
    result = prompts_col.find_one_and_update(
        {'_id': ObjectId(pid)},
        {'$pull': {'comments': {'_id': cid}}},
        return_document=True
    )
    if result is None:
        return '', 404
    return '', 204

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 3000)))
