import argparse
import signal
import threading
from acompanhamento.moodle import MoodleClient
from acompanhamento.service import scan
from infra.broker import Broker
from infra.config import Settings
from infra.health import Health
from infra.logging import configure, log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Executa um ciclo e encerra")
    args = parser.parse_args()
    configure()
    settings = Settings.load()
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    health = Health("acompanhamento")
    health.max_age = settings.interval * 2 + 60
    server = health.start(settings.health_port) if not args.once else None
    try:
        while not stop.is_set():
            try:
                # Conexões curtas evitam perder heartbeat durante a espera de uma hora.
                events = scan(MoodleClient(settings), settings)
                with Broker(settings) as broker:
                    for event in events:
                        broker.publish(event.encode(), event.event_id)
                        log("solicitacao_publicada", event_id=event.event_id)
                log("ciclo_concluido", published=len(events))
                health.success()
            except Exception as exc:
                health.ready = False
                log("ciclo_falhou", error_type=type(exc).__name__)
                if args.once:
                    return 1
            if args.once:
                return 0
            stop.wait(settings.interval if health.ready else min(settings.interval, 30))
    finally:
        if server:
            server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
