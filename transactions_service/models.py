from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    def __repr__(self):
        return f'<Expense {self.id}: {self.amount} in {self.category} on {self.date}>'