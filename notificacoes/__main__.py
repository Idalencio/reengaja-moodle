import signal
import threading
from infra.broker import Broker
from infra.config import Settings
from infra.health import Health
from infra.logging import configure, log
from notificacoes.mailer import SmtpMailer
from notificacoes.service import Handler
from notificacoes.store import Store


def main():
    configure()
    settings = Settings.load()
    store = Store(settings.database)
    health = Health("notificacoes")
    server = health.start(settings.health_port)
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    try:
        while not stop.is_set():
            try:
                with Broker(settings) as broker:
                    handler = Handler(broker, store, SmtpMailer(settings), settings)
                    health.success()
                    for method, properties, body in broker.channel.consume(broker.main, inactivity_timeout=1, auto_ack=False):
                        if method:
                            handler(broker.channel, method, properties, body)
                        if stop.is_set():
                            break
                    broker.channel.cancel()
            except Exception as exc:
                health.ready = False
                log("consumidor_reconectando", error_type=type(exc).__name__)
                stop.wait(5)
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
