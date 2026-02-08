import time
import uuid
from json import loads

from framework.internal.http.account import AccountApi
from framework.internal.http.mail import MailApi
from framework.internal.kafka.producer import Producer



# Тесты на проверку асинхронной регистрации Kafka Topic: register-events-errors
# Проверка с отправкой сообщения в топик register-events-error и активацией токена
def test_register_events_error_consumer(account: AccountApi, mail: MailApi, kafka_producer: Producer) -> None:
    base = uuid.uuid4().hex
    message = {
      "input_data": {
        "login": base,
        "email": f"{base}@mail.ru",
        "password": "123123123"
      },
      "error_message": {
        "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
        "title": "Validation failed",
        "status": 400,
        "traceId": "00-2bd2ede7c3e4dcf40c4b7a62ac23f448-839ff284720ea656-01",
        "errors": {
          "Email": [
            "Invalid"
          ]
        }
      },
      "error_type": "unknown"
    }

    kafka_producer.send('register-events-errors', message)
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













