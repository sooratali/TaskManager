# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import models
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for sessions (ok for local testing)

# ensure DB is initialized
models.init_db()

# Helper to get current user id
def current_user_id():
    if 'user_email' in session:
        row = models.get_user_by_email(session['user_email'])
        if row:
            return row['id']
    return None

@app.route('/')
def index():
    uid = current_user_id()
    if not uid:
        return redirect(url_for('login'))
    tasks = models.get_tasks_for_user(uid)
    return render_template('index.html', tasks=tasks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('register'))
        if models.find_user_by_email(email):
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('login'))
        models.create_user(email, password)
        flash('Account created. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if models.verify_user(email, password):
            session['user_email'] = email
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/task/new', methods=['GET','POST'])
def task_new():
    uid = current_user_id()
    if not uid:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        description = request.form.get('description','').strip()
        due_date = request.form.get('due_date','').strip()
        priority = request.form.get('priority','Normal')
        if not title:
            flash('Title is required.', 'error')
            return redirect(url_for('task_new'))
        models.create_task(uid, title, description, due_date, priority)
        flash('Task created.', 'success')
        return redirect(url_for('index'))
    return render_template('task_form.html', task=None, action='Create')

@app.route('/task/edit/<int:task_id>', methods=['GET','POST'])
def task_edit(task_id):
    uid = current_user_id()
    if not uid:
        return redirect(url_for('login'))
    task = models.get_task(task_id)
    if not task or task['user_id'] != uid:
        flash('Task not found.', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        description = request.form.get('description','').strip()
        due_date = request.form.get('due_date','').strip()
        priority = request.form.get('priority','Normal')
        status = request.form.get('status','incomplete')
        if not title:
            flash('Title is required.', 'error')
            return redirect(url_for('task_edit', task_id=task_id))
        models.update_task(task_id, title, description, due_date, priority, status)
        flash('Task updated.', 'success')
        return redirect(url_for('index'))
    return render_template('task_form.html', task=task, action='Edit')

@app.route('/task/delete/<int:task_id>', methods=['POST'])
def task_delete(task_id):
    uid = current_user_id()
    if not uid:
        return redirect(url_for('login'))
    task = models.get_task(task_id)
    if task and task['user_id'] == uid:
        models.delete_task(task_id)
        flash('Task deleted.', 'success')
    else:
        flash('Task not found or permission denied.', 'error')
    return redirect(url_for('index'))

@app.route('/task/toggle/<int:task_id>', methods=['POST'])
def task_toggle(task_id):
    uid = current_user_id()
    if not uid:
        return redirect(url_for('login'))
    task = models.get_task(task_id)
    if task and task['user_id'] == uid:
        new_status = 'complete' if task['status'] == 'incomplete' else 'incomplete'
        models.update_task(task_id, task['title'], task['description'], task['due_date'], task['priority'], new_status)
        flash('Task status updated.', 'success')
    else:
        flash('Task not found or permission denied.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # for local development only
    app.run(debug=True)
