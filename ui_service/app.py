from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ui-secret-key-change-in-prod'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


AUTH_URL = os.getenv('AUTH_URL')
TRANSACTIONS_URL = os.getenv('TRANSACTIONS_URL')
REPORTS_URL = os.getenv('REPORTS_URL')

@app.route('/')
def index():
    if 'token' in session:
        return redirect(url_for('expenses'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        resp = requests.post(f'{AUTH_URL}/login', json=request.form)
        if resp.status_code == 200:
            data = resp.json()
            session['token'] = data['access_token']
            session['user_id'] = data['user_id']
            flash('Успешный логин!', 'success')
            return redirect(url_for('expenses'))
        flash('Неверные данные', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        resp = requests.post(f'{AUTH_URL}/register', json=request.form)
        if resp.status_code == 201:
            flash('Регистрация успешна! Войдите.', 'success')
            return redirect(url_for('login'))
        flash('Ошибка регистрации', 'error')
    return render_template('register.html')

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if 'token' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    token = session['token']
    headers = {'Authorization': f'Bearer {token}'}

    if request.method == 'POST':
        resp = requests.post(f'{TRANSACTIONS_URL}/expenses', json=request.form, headers=headers)
        if resp.status_code == 201:
            flash('Расход добавлен!', 'success')

    resp = requests.get(f'{TRANSACTIONS_URL}/expenses/{user_id}', headers=headers)
    expenses_data = resp.json() if resp.status_code == 200 else []

    return render_template('expenses.html', expenses=expenses_data)

@app.route('/reports')
def reports():
    if 'token' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    token = session['token']
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(f'{REPORTS_URL}/reports/{user_id}?period=month', headers=headers)
    reports_data = resp.json() if resp.status_code == 200 else []

    return render_template('reports.html', reports=reports_data)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)