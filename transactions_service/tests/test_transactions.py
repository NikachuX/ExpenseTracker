import pytest
from models import db, Expense
from app import create_app
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'JWT_SECRET_KEY': 'test-secret'
    }
    app_instance = create_app(test_config)
    with app_instance.app_context():
        db.create_all()
    yield app_instance
    with app_instance.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token(app):
    with app.app_context():
        return create_access_token(identity='1')  # user_id=1

def test_add_expense(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/expenses', json={'amount': 150.5, 'category': 'Еда'}, headers=headers)
    assert response.status_code == 201
    assert response.json['message'] == 'Расход добавлен'
    with client.application.app_context():
        expense = Expense.query.first()
        assert expense.amount == 150.5
        assert expense.category == 'Еда'

def test_get_expenses(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    client.post('/expenses', json={'amount': 100, 'category': 'Транспорт'}, headers=headers)
    response = client.get('/expenses/1', headers=headers)
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]['category'] == 'Транспорт'

def test_get_unauthorized(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/expenses/2', headers=headers)  # Чужой user_id
    assert response.status_code == 403