import pika


class Broker:
    def __init__(self, settings):
        self.settings = settings
        self.main = settings.queue_prefix + ".solicitacoes"
        self.retry = settings.queue_prefix + ".retry"
        self.dead = settings.queue_prefix + ".dead"
        self.connection = None
        self.channel = None

    def __enter__(self):
        parameters = pika.URLParameters(self.settings.amqp_url)
        parameters.heartbeat = 60
        parameters.blocked_connection_timeout = 20
        parameters.socket_timeout = 10
        parameters.stack_timeout = 15
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        try:
            self.declare()
        except Exception:
            self.connection.close()
            raise
        return self

    def declare(self):
        self.channel.queue_declare(queue=self.main, durable=True)
        self.channel.queue_declare(queue=self.dead, durable=True)
        self.channel.queue_declare(queue=self.retry, durable=True, arguments={
            "x-message-ttl": self.settings.retry_delay_ms,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": self.main,
        })
        self.channel.confirm_delivery()
        self.channel.basic_qos(prefetch_count=1)

    def publish(self, body, event_id=None, queue=None):
        self.channel.basic_publish(
            exchange="", routing_key=queue or self.main, body=body, mandatory=True,
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2,
                                            message_id=event_id, type="reengajamento.v1"),
        )

    def __exit__(self, *_):
        if self.connection and self.connection.is_open:
            self.connection.close()
