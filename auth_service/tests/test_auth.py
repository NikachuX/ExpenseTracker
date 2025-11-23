import pytest
from app import create_app
from models import db, User

@pytest.fixture
def app():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'JWT_SECRET_KEY': 'test-secret'
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/register', json={'email': 'test@example.com', 'password': '123456'})
    assert response.status_code == 201
    assert response.json == {'message': 'Пользователь зарегистрирован'}

def test_register_duplicate(client):
    client.post('/register', json={'email': 'dup@example.com', 'password': '123456'})
    response = client.post('/register', json={'email': 'dup@example.com', 'password': '123456'})
    assert response.status_code == 400
    assert 'Пользователь уже существует' in response.json['error']

def test_login(client):
    client.post('/register', json={'email': 'login@example.com', 'password': '123456'})
    response = client.post('/login', json={'email': 'login@example.com', 'password': '123456'})
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'user_id' in response.json