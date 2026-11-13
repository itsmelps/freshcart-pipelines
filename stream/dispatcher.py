import argparse
import json
import os
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

import pika


EXCHANGE_NAME = "rapido-dispatch"
ZONES = {
    "bangalore": ("koramangala", "indiranagar", "whitefield"),
    "chennai": ("tnagar", "anna_nagar", "velachery"),
}
ORDER_TYPES = ("ride", "food")


def create_message(sequence, city, zone, order_type):
    message = {
        "id": f"{sequence}-{uuid4().hex[:8]}",
        "city": city,
        "zone": zone,
        "type": order_type,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if sequence % 10 == 0:
        del message["zone"]
    return message


def main():
    parser = argparse.ArgumentParser(description="Publish food-order requests.")
    parser.add_argument(
        "--routing-key",
        help="Publish one specific three-word key, then exit (for routing demonstrations).",
    )
    args = parser.parse_args()

    if args.routing_key:
        parts = args.routing_key.split(".")
        if len(parts) != 3 or not all(parts):
            parser.error("--routing-key must have exactly three non-empty words")
        test_city, test_zone, test_type = parts
        requests = [(1, test_city, test_zone, test_type)]
    else:
        requests = None

    amqp_url = os.environ.get(
        "AMQP_URL", "amqp://guest:guest@localhost:5672/%2F"
    )
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    try:
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
        )

        sequence = 1
        while True:
            if requests is None:
                city = random.choice(tuple(ZONES))
                zone = random.choice(ZONES[city])
                order_type = random.choice(ORDER_TYPES)
            else:
                _, city, zone, order_type = requests[0]

            routing_key = f"{city}.{zone}.{order_type}"
            message = create_message(sequence, city, zone, order_type)
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    content_type="application/json", delivery_mode=2
                ),
            )
            print(
                f"[PUBLISHED] id={message['id']} "
                f"routing_key={routing_key} payload={json.dumps(message)}",
                flush=True,
            )
            if requests is not None:
                break

            sequence += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nDispatcher stopped.", flush=True)
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
