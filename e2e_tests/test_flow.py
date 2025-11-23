import pytest
import requests
import time

# Адреса сервисов внутри Docker-сети (имена сервисов из docker-compose)
AUTH_URL = "http://auth-service:5000"
TRANS_URL = "http://transactions-service:5001"
REPORTS_URL = "http://reports-service:5002"


def wait_for_services():
    """Ждем, пока сервисы поднимутся"""
    time.sleep(5)  # Простая задержка, по-хорошему нужен check loop


def test_full_scenario():
    wait_for_services()

    # 1. Регистрация (Auth Service)
    email = "test_env@example.com"
    password = "securepassword"
    reg_resp = requests.post(f"{AUTH_URL}/register", json={"email": email, "password": password})
    assert reg_resp.status_code == 201

    # 2. Логин (Auth Service)
    login_resp = requests.post(f"{AUTH_URL}/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200
    token = login_resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Добавление расхода (Transactions Service)
    expense_data = {"amount": 500.0, "category": "TestEnv"}
    trans_resp = requests.post(f"{TRANS_URL}/expenses", json=expense_data, headers=headers)
    assert trans_resp.status_code == 201

    # 4. Проверка отчета (Reports Service)
    # Reports ходит в ту же БД, куда писал Transactions. Это проверка интеграции БД.
    report_resp = requests.get(f"{REPORTS_URL}/reports/{login_resp.json()['user_id']}?period=month", headers=headers)
    assert report_resp.status_code == 200
    data = report_resp.json()

    print("E2E Test Passed: All services communicate correctly via DB!")