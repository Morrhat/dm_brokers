import json
import uuid

from kafka import KafkaConsumer

from framework.internal.kafka.producer import Producer



# Тесты на проверку асинхронной регистрации с консумером
#
def test_success_registration_with_kafka_producer_consumer(kafka_producer: Producer) -> None:
    base = uuid.uuid4().hex
    message = {
              "login": base,
              "email": f"{base}@mail.ru",
              "password": "123123123"
            }
    kafka_producer.send('register-events', message)

    consumer = KafkaConsumer(
        'register-events',
    bootstrap_servers=['185.185.143.231:9092'],
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    )

    for message in consumer:
        if message.value["login"] == base:
            break

    consumer.close()

