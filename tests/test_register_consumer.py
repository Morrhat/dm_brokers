import json
import uuid
import time

from kafka import KafkaConsumer

from framework.internal.kafka.consumer import Consumer
from framework.internal.kafka.producer import Producer



# Тесты на проверку асинхронной регистрации с классом консумером
#
def test_success_registration_with_kafka_producer_consumer(
        kafka_consumer: Consumer,
        kafka_producer: Producer
) -> None:
    base = uuid.uuid4().hex
    message = {
              "login": base,
              "email": f"{base}@mail.ru",
              "password": "123123123"
            }
    kafka_producer.send('register-events', message)
    for i in range(10):
        message = kafka_consumer.get_message()
        if message.value["login"] == base:
            break
    else:
        raise AssertionError("Email not found")

