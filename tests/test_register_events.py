import time
import uuid
from json import loads

from framework.internal.http.account import AccountApi
from framework.internal.http.mail import MailApi
from framework.internal.kafka.producer import Producer



# Тесты на проверку асинхронной регистрации Kafka Topic: register-events
# Проверка успешной асинхронной регистрации пользователя
def test_success_registration_with_kafka_producer(mail: MailApi, kafka_producer: Producer) -> None:
    base = uuid.uuid4().hex
    message = {
              "login": base,
              "email": f"{base}@mail.ru",
              "password": "123123123"
            }
    kafka_producer.send('register-events', message)
    for _ in range(10):
        response = mail.find_message(query=base)
        if response.json()["total"] > 0:
            break
        time.sleep(1)
    else:
        raise AssertionError("Email not found")


# Проверка успешной асинхронной регистрации пользователя с активацией токена
def test_success_activation_with_kafka_producer(account: AccountApi, mail: MailApi, kafka_producer: Producer) -> None:
    base = uuid.uuid4().hex
    message = {
              "login": base,
              "email": f"{base}@mail.ru",
              "password": "123123123"
            }
    kafka_producer.send('register-events', message)
    for _ in range(10):
        response = mail.find_message(query=base)
        if response.json()["total"] > 0:
            break
        time.sleep(1)
    else:
        raise AssertionError("Email not found")

    # Получение токена
    token = None
    for item in response.json()["items"]:
        user_data = loads(item["Content"]["Body"])
        token = user_data["ConfirmationLinkUrl"].split("/")[-1]
    assert token is not None, f"Токен активации не был получен"
    print("Токен активации")
    print(token)

    # Активация пользователя
    response = account.activate_user(token)
    if response.status_code == 200:
        print(response.status_code)
        print("Пользователь активирован")
    else:
        raise AssertionError("Пользователь не активирован")
