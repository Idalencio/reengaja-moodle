from infra.events import Reminder
from infra.logging import log


class Handler:
    def __init__(self, broker, store, mailer, settings):
        self.broker, self.store, self.mailer, self.settings = broker, store, mailer, settings

    def __call__(self, channel, method, properties, body):
        try:
            event = Reminder.decode(body)
        except ValueError:
            self.broker.publish(body, queue=self.broker.dead)
            log("mensagem_invalida", reason="contrato_invalido")
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return
        result = self.store.process(event, self.mailer, self.settings.max_attempts)
        if result.status == "retry":
            # Se publicar falhar, a original fica sem ACK e volta após a reconexão.
            self.broker.publish(body, event.event_id, self.broker.retry)
        elif result.status == "dead":
            self.broker.publish(body, event.event_id, self.broker.dead)
        log("notificacao_" + result.status, event_id=event.event_id, attempts=result.attempts,
            error_type=result.error_type)
        channel.basic_ack(delivery_tag=method.delivery_tag)
