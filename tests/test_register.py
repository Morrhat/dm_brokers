import time
import uuid
from json import loads

from framework.internal.http.account import AccountApi
from framework.internal.http.mail import MailApi



# Проверка неудачной регистрации пользователя
def test_failed_registration(account: AccountApi, mail: MailApi) -> None:
    expected_mail = "string@mail.ru"
    account.register_user(login="string", email=expected_mail, password="string")

    for _ in range(10):
        response = mail.find_message(query=expected_mail)
        if response.json()["total"] > 0:
            raise AssertionError("Email found")
        time.sleep(1)
    else:
        print("No email found. Test PASSED")


# Проверка успешной регистрации пользователя
def test_successful_registration(account: AccountApi, mail: MailApi) -> None:
    base = uuid.uuid4().hex
    account.register_user(login=base, email=f"{base}@mail.ru", password="123123123")

    for _ in range(10):
        response = mail.find_message(query=base)
        if response.json()["total"] > 0:
            break
        time.sleep(1)
    else:
        raise AssertionError("Email not found")


# Проверка успешной регистрации пользователя с активацией токена
def test_successful_activation(account: AccountApi, mail: MailApi) -> None:
    base = uuid.uuid4().hex
    account.register_user(login=base, email=f"{base}@mail.ru", password="123123123")

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
    assert token is not None, f"Токен сброса пароля не был получен"
    print("Токен активации")
    print(token)

    # Активация пользователя
    response = account.activate_user(token)
    if response.status_code == 200:
        print(response.status_code)
        print("Пользователь активирован")
    else:
        raise AssertionError("Пользователь не активирован")