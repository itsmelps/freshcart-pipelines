import json
import os
import sys

import pika


EXCHANGE_NAME = "rapido-dispatch"


def process_request(channel, driver_name, method, body):
    try:
        request = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        print(
            f"[NACK discard] driver={driver_name} reason=invalid JSON ({error})",
            flush=True,
        )
        return

    if not isinstance(request, dict) or "zone" not in request:
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        print(
            f"[NACK discard] driver={driver_name} "
            f"routing_key={method.routing_key} reason=missing zone "
            f"payload={body.decode('utf-8', errors='replace')}",
            flush=True,
        )
        return

    print(
        f"[RECEIVED] driver={driver_name} routing_key={method.routing_key} "
        f"request={json.dumps(request)}",
        flush=True,
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)
    print(f"[ACK] driver={driver_name} id={request.get('id')}", flush=True)


def main():
    if len(sys.argv) != 3:
        print("Usage: python stream/driver.py NAME PATTERN", file=sys.stderr)
        return 2

    name, pattern = sys.argv[1:]
    amqp_url = os.environ.get(
        "AMQP_URL", "amqp://guest:guest@localhost:5672/%2F"
    )
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    try:
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
        )
        result = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
        queue_name = result.method.queue
        channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=queue_name, routing_key=pattern
        )
        print(
            f"[READY] driver={name} queue={queue_name} binding={pattern}",
            flush=True,
        )

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, properties, body: process_request(
                ch, name, method, body
            ),
            auto_ack=False,
        )
        print(f"Driver {name} waiting for requests. Press Ctrl+C to stop.", flush=True)
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\nDriver {name} stopped.", flush=True)
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
