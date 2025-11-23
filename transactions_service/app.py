from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from models import db, Expense
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    if test_config:
        app.config.update(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    db.init_app(app)
    jwt = JWTManager(app)

    @app.route('/expenses', methods=['POST'])
    @jwt_required()
    def add_expense():
        user_id = int(get_jwt_identity())  # Из токена (строка → int)
        data = request.get_json()
        amount = data.get('amount')
        category = data.get('category')
        expense_date = data.get('date', date.today().isoformat())  # По умолчанию сегодня

        if not amount or not category:
            return jsonify({'error': 'Сумма и категория обязательны'}), 400

        # Валидация: Простая проверка user_id > 0 (в prod — вызов к Auth)
        if user_id <= 0:
            return jsonify({'error': 'Неверный пользователь'}), 400

        expense = Expense(
            user_id=user_id,
            amount=float(amount),
            category=category,
            date=date.fromisoformat(expense_date)
        )
        db.session.add(expense)
        db.session.commit()

        return jsonify({'message': 'Расход добавлен', 'id': expense.id}), 201


    @app.route('/expenses/<int:user_id>', methods=['GET'])
    @jwt_required()
    def get_expenses(user_id):
        if int(get_jwt_identity()) != user_id:
            return jsonify({'error': 'Access denied'}), 403  # Только свои расходы

        expenses = Expense.query.filter_by(user_id=user_id).all()
        return jsonify([
            {
                'id': e.id,
                'amount': e.amount,
                'category': e.category,
                'date': e.date.isoformat()
            }
            for e in expenses
        ])


    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'OK'})

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)