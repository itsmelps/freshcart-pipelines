import json
from types import SimpleNamespace

from stream.dispatcher import create_message
from stream.driver import process_request


class RecordingChannel:
    def __init__(self):
        self.acknowledged = []
        self.rejected = []

    def basic_ack(self, delivery_tag):
        self.acknowledged.append(delivery_tag)

    def basic_nack(self, delivery_tag, requeue):
        self.rejected.append((delivery_tag, requeue))


def test_dispatcher_omits_zone_from_every_tenth_message():
    good_message = create_message(9, "bangalore", "koramangala", "food")
    bad_message = create_message(10, "bangalore", "koramangala", "food")

    assert good_message["zone"] == "koramangala"
    assert "zone" not in bad_message
    assert {"id", "city", "type", "ts"} <= bad_message.keys()


def test_driver_acknowledges_message_with_zone():
    channel = RecordingChannel()

    process_request(
        channel,
        "Ravi",
        SimpleNamespace(delivery_tag=1, routing_key="bangalore.koramangala.food"),
        json.dumps({"id": "request-1", "zone": "koramangala"}).encode(),
    )

    assert channel.acknowledged == [1]
    assert channel.rejected == []


def test_driver_discards_message_without_zone():
    channel = RecordingChannel()

    process_request(
        channel,
        "Ravi",
        SimpleNamespace(delivery_tag=2, routing_key="bangalore.koramangala.food"),
        json.dumps({"id": "request-2"}).encode(),
    )

    assert channel.acknowledged == []
    assert channel.rejected == [(2, False)]
