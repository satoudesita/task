from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os

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
    return jsonify({"message": "Task added successfully", "task": new_task}), 201

@app.route('/tasks/<int:task_index>', methods=['DELETE'])
def delete_task(task_index):
    if task_index < 0 or task_index >= len(data):
        return jsonify({"error": "Task not found"}), 404
    deleted_task = data.pop(task_index)
    save_data()
    return jsonify({"message": "Task deleted successfully", "task": deleted_task}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)