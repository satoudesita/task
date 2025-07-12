from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os
import requests #powerAutomate用はお追加

app = Flask(__name__)
DATA_FILE = 'tasks.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(data)

@app.route('/tasks', methods=['POST'])
def add_task():
    new_task = request.json

    required_fields = {"name", "url", "detail"}
    if not required_fields.issubset(new_task):
        return jsonify({"error": "Missing required fields"}), 400

    if "date" not in new_task:
        new_task["date"] = datetime.utcnow().strftime('%Y-%m-%d')
    else:
        try:
            parsed_date = datetime.strptime(new_task["date"], '%Y-%m-%d')
            new_task["date"] = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    data.append(new_task)
    save_data()

    #はおここからpowerAutomate追加
    url = 'https://prod-36.japaneast.logic.azure.com:443/workflows/fe79560e4d0549c0a28054d8f3ac8faa/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=X4cU73v5T7vx1OYxYCRqHcyxGvPxiTGfDN-HpfbC46U'
    notify_data = new_task.copy()
    notify_data["動作"] = "追加"
    try:
        response = requests.post(url,json=notify_data)
        response.raise_for_status()
    except Exception as e:
        print("Teamsの送信に失敗", e)
    #ここまで
    return jsonify({"message": "Task added successfully", "task": new_task}), 201

@app.route('/tasks/<int:task_index>', methods=['DELETE'])
def delete_task(task_index):
    if task_index < 0 or task_index >= len(data):
        return jsonify({"error": "Task not found"}), 404
    deleted_task = data.pop(task_index)
    save_data()

    #はおここからpowerAutomate追加
    url = 'https://prod-36.japaneast.logic.azure.com:443/workflows/fe79560e4d0549c0a28054d8f3ac8faa/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=X4cU73v5T7vx1OYxYCRqHcyxGvPxiTGfDN-HpfbC46U'
    notify_data = deleted_task.copy()
    notify_data["動作"] = "削除"
    try:
        response = requests.post(url,json=notify_data)
        response.raise_for_status()
    except Exception as e:
        print("Teamsの送信に失敗", e)
    #ここまで

    return jsonify({"message": "Task deleted successfully", "task": deleted_task}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)