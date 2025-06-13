from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import urllib.request, json
import requests

app = Flask(__name__)

@app.route('/')
def index():
    todos = {}

    try:
        # URL du backend
        url = "http://localhost:5000/"
        response = requests.get(url, timeout=60)
        todos = json.loads(response.content)
    except Exception as ex:
        exc = str(ex)

    return render_template('index.html', todos=todos)

@app.route('/create', methods=['POST'])
def create():
    task = request.form.get('task')
    try:
        url = "http://localhost:5000/create"
        data = {'task': task}
        response = requests.post(url, data=data)
        return redirect('/')
    except Exception as ex:
        exc = str(ex)
        return redirect('/')

@app.route('/update', methods=['POST'])
def update():
    task_id = request.form.get('task_id')
    task = request.form.get('task')
    try:
        url = "http://localhost:5000/update"
        data = {'task_id': task_id, 'task': task}
        response = requests.post(url, data=data)
        return redirect('/')
    except Exception as ex:
        exc = str(ex)
        return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=False)
