"""Integração real HTTP + AMQP + SMTP, com Moodle de demonstração explicitamente simulado.

Não usa mocks de broker/SMTP. Usa filas exclusivas da execução e destinatários fictícios.
"""
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import urlopen
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acompanhamento.moodle import MoodleClient
from acompanhamento.service import scan
from infra.broker import Broker
from infra.config import Settings
from notificacoes.mailer import SmtpMailer
from notificacoes.service import Handler
from notificacoes.store import Store


def json_get(url):
    with urlopen(url, timeout=10) as response:
        return json.load(response)


def pump(broker, handler, count, timeout=12):
    deadline = time.monotonic() + timeout
    received = 0
    while received < count and time.monotonic() < deadline:
        method, properties, body = broker.channel.basic_get(broker.main, auto_ack=False)
        if method:
            handler(broker.channel, method, properties, body)
            received += 1
        else:
            broker.connection.process_data_events(time_limit=0.1)
            time.sleep(0.05)
    assert received == count, f"Esperadas {count} mensagens, recebidas {received}"


def execute(output="evidencias"):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex[:10]
    api = os.getenv("MAILPIT_API", "http://127.0.0.1:8025").rstrip("/")
    base = Settings.load()
    results = []

    def check(identifier, description, assertion, detail):
        assert assertion, description
        results.append({"id": identifier, "description": description, "passed": True, "detail": detail})
        print(f"PASS {identifier}: {description}", flush=True)

    def messages():
        query = urlencode({"query": f"to:{token}", "limit": 100})
        return json_get(api + "/api/v1/search?" + query)["messages"]

    # Aguarda a API SMTP/HTTP, pois o Compose pode iniciar o contêiner antes de ficar pronto.
    for attempt in range(30):
        try:
            json_get(api + "/api/v1/messages")
            break
        except OSError:
            if attempt == 29:
                raise
            time.sleep(1)

    with tempfile.TemporaryDirectory(prefix="reengaja-e2e-") as temp:
        settings = replace(base, queue_prefix="e2e." + token, retry_delay_ms=500,
                           database=str(Path(temp) / "notificacoes.sqlite3"), smtp_timeout=2, max_attempts=3)
        events = scan(MoodleClient(settings), settings)
        # Apenas o endereço fictício recebe etiqueta para isolar evidências de execuções anteriores.
        events = [replace(e, student_email=e.student_email.replace("@", f"+{token}@")) for e in events]
        check("I01", "Somente Ana pendente e Carla em rascunho são selecionadas",
              {e.student_id for e in events} == {101, 103} and {e.assignment_id for e in events} == {501},
              {"events": [e.event_id for e in events], "expected_students": [101, 103]})
        store = Store(settings.database)
        with Broker(settings) as broker:
            handler = Handler(broker, store, SmtpMailer(settings), settings)
            try:
                for event in events:
                    broker.publish(event.encode(), event.event_id)
                pump(broker, handler, 2)
                received = messages()
                check("I02", "Dois lembretes chegam ao Mailpit por SMTP", len(received) == 2,
                      {"mailpit_messages": len(received)})
                for event in events:
                    broker.publish(event.encode(), event.event_id)
                pump(broker, handler, 2)
                check("I03", "Reprocessar mensagens concluídas não gera e-mail", len(messages()) == 2,
                      {"mailpit_messages_after_replay": len(messages())})
                restarted = Handler(broker, Store(settings.database), SmtpMailer(settings), settings)
                for event in events:
                    broker.publish(event.encode(), event.event_id)
                pump(broker, restarted, 2)
                check("I04", "Histórico continua válido após reabrir o banco", len(messages()) == 2,
                      {"mailpit_messages_after_store_reopen": len(messages())})

                with socket.socket() as probe:
                    probe.bind(("127.0.0.1", 0))
                    closed_port = probe.getsockname()[1]
                failing = replace(settings, smtp_host="127.0.0.1", smtp_port=closed_port)
                failing_handler = Handler(broker, store, SmtpMailer(failing), settings)
                retry_event = replace(events[0], student_id=104, student_name="Davi Exemplo",
                                      student_email=f"davi+{token}@example.test")
                broker.publish(retry_event.encode(), retry_event.event_id)
                pump(broker, failing_handler, 1)
                with sqlite3.connect(settings.database) as db:
                    row = db.execute("SELECT status,attempts,error_type FROM deliveries WHERE event_id=?", (retry_event.event_id,)).fetchone()
                check("I05", "Conexão SMTP recusada registra falha e encaminha para retry", row[:2] == ("retry", 1),
                      {"status": row[0], "attempts": row[1], "error_type": row[2], "retry_delay_ms": 500})
                pump(broker, handler, 1)
                with sqlite3.connect(settings.database) as db:
                    row = db.execute("SELECT status,attempts FROM deliveries WHERE event_id=?", (retry_event.event_id,)).fetchone()
                check("I06", "Após o TTL a mensagem retorna e o SMTP funciona", row == ("sent", 2) and len(messages()) == 3,
                      {"status": row[0], "attempts": row[1], "mailpit_messages": len(messages())})

                expired = replace(events[0], student_id=105, due_at=int(time.time()) - 1)
                broker.publish(expired.encode(), expired.event_id)
                pump(broker, handler, 1)
                check("I07", "Mensagem que vence enquanto espera na fila não é enviada", len(messages()) == 3,
                      {"mailpit_messages": len(messages())})

                broker.publish(b'{"invalido":true}')
                pump(broker, handler, 1)
                dead_count = broker.channel.queue_declare(broker.dead, passive=True).method.message_count
                check("I08", "Contrato inválido vai para fila de falhas", dead_count == 1,
                      {"dead_messages": dead_count})

                exhausted = replace(retry_event, student_id=106, student_email=f"erica+{token}@example.test")
                broker.publish(exhausted.encode(), exhausted.event_id)
                pump(broker, failing_handler, 3)
                with sqlite3.connect(settings.database) as db:
                    row = db.execute("SELECT status,attempts FROM deliveries WHERE event_id=?", (exhausted.event_id,)).fetchone()
                dead_count = broker.channel.queue_declare(broker.dead, passive=True).method.message_count
                check("I09", "Três falhas encerram tentativas e preservam mensagem na DLQ",
                      row == ("dead", 3) and dead_count == 2, {"status": row[0], "attempts": row[1], "dead_messages": dead_count})

                with sqlite3.connect(settings.database) as db:
                    deliveries = [dict(zip(["event_id", "status", "attempts", "error_type"], row))
                                  for row in db.execute("SELECT event_id,status,attempts,error_type FROM deliveries ORDER BY event_id")]
                    audit = [dict(zip(["event_id", "outcome", "attempts", "error_type", "recorded_at"], row))
                             for row in db.execute("SELECT event_id,outcome,attempts,error_type,recorded_at FROM audit ORDER BY id")]
                received = messages()
                for i, message in enumerate(received, 1):
                    with urlopen(api + "/api/v1/message/" + message["ID"] + "/raw", timeout=10) as response:
                        (output / f"email_{i}.eml").write_bytes(response.read())
                result = {"executed_at": datetime.now(timezone.utc).isoformat(), "run_id": token,
                          "environment": {"moodle": "simulador HTTP do contrato REST; não é instalação Moodle",
                                          "broker": "RabbitMQ real por AMQP 0-9-1", "smtp": "Mailpit real por SMTP",
                                          "python": sys.version.split()[0]},
                          "passed": len(results), "failed": 0, "cases": results,
                          "deliveries": deliveries, "audit": audit, "emails": received,
                          "limitations": ["Docker Compose e Moodle institucional exigem validação no ambiente de destino.",
                                          "Não existe atomicidade entre a aceitação SMTP e o commit SQLite."]}
                (output / "integracao.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
                (output / "evento_exemplo.json").write_bytes(events[0].encode())
                return result
            finally:
                # Só remove as filas e2e criadas por esta execução; não toca nas filas da aplicação.
                for queue in (broker.retry, broker.main, broker.dead):
                    broker.channel.queue_delete(queue=queue)


if __name__ == "__main__":
    result = execute(os.getenv("EVIDENCE_DIR", "evidencias"))
    print(f"Integração: {result['passed']} casos aprovados, {result['failed']} falhas.")
