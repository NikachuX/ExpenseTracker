from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Импорт модели Expense из Transactions (для запросов)
class Expense(db.Model):  # Дублируем для простоты; в prod — shared models
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)