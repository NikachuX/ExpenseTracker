import pytest
from models import db, Expense
from app import create_app

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

def health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'OK'}