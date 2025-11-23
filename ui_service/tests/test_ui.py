import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


@patch('requests.post')  # Мок API-вызовов
@patch('requests.get')
def test_login(mock_get, mock_post, client):
    # Мок ответа от Auth
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'access_token': 'fake', 'user_id': 1}

    response = client.post('/login', data={'email': 'test@example.com', 'password': '123456'})
    assert response.status_code == 302  # Redirect
    assert 'expenses' in response.headers['Location']  # Редирект после успеха


@patch('requests.post')
def test_register(mock_post, client):
    mock_post.return_value.status_code = 201

    response = client.post('/register', data={'email': 'new@example.com', 'password': '123456'})
    assert response.status_code == 302
    assert 'login' in response.headers['Location']


@patch('requests.post')
@patch('requests.get')
def test_expenses(mock_get, mock_post, client):
    # Мок сессии: Устанавливаем токен вручную
    with client.session_transaction() as sess:
        sess['token'] = 'fake'
        sess['user_id'] = 1

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{'id': 1, 'amount': 100}]

    response = client.get('/expenses')
    assert response.status_code == 200
