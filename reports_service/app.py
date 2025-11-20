from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from models import db, Expense
from sqlalchemy import func, extract
import os
from dotenv import load_dotenv
import time
from sqlalchemy.exc import OperationalError
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
jwt = JWTManager(app)


# Retry для БД
# def wait_for_db():
#     max_retries = 10
#     for i in range(max_retries):
#         try:
#             with app.app_context():
#                 db.engine.execute("SELECT 1")
#             print(f"БД готова! (попытка {i + 1})")
#             with app.app_context():
#                 db.create_all()
#             return True
#         except OperationalError as e:
#             print(f"БД не готова... Ошибка: {e}. Ждём 3 сек (попытка {i + 1}/{max_retries})")
#             time.sleep(3)
#     raise Exception(f"Не удалось подключиться к БД после {max_retries} попыток.")


@app.route('/reports/<int:user_id>', methods=['GET'])
@jwt_required()
def get_report(user_id):
    if int(get_jwt_identity()) != user_id:
        return jsonify({'error': 'Доступ запрещён'}), 403

    period = request.args.get('period', 'month')  # month, week, year

    query = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(Expense.user_id == user_id)

    # Фильтр по периоду
    now = datetime.now()
    if period == 'month':
        query = query.filter(
            extract('year', Expense.date) == now.year,
            extract('month', Expense.date) == now.month
        )
    elif period == 'week':
        # Неделя: упрощённо, последние 7 дней
        query = query.filter(Expense.date >= now.date() - timedelta(days=7))
    elif period == 'year':
        query = query.filter(extract('year', Expense.date) == now.year)
    else:
        return jsonify({'error': 'Неверный период: month/week/year'}), 400

    query = query.group_by(Expense.category).order_by(func.sum(Expense.amount).desc())
    results = query.all()

    return jsonify([
        {
            'category': r.category,
            'total': float(r.total)
        }
        for r in results
    ])


# Health
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})


if __name__ == '__main__':
    #wait_for_db()
    app.run(debug=True, host='0.0.0.0', port=5002)