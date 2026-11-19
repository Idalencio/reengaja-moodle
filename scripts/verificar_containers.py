"""Confere a composição em execução. Usa apenas a biblioteca padrão do Python.

Executar após docker compose up -d --build --wait, em uma demonstração nova.
Os registros só indicam sucesso depois de todas as verificações reais.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def compose(*args):
    return subprocess.check_output(["docker", "compose", *args], cwd=ROOT, text=True).strip()


def get_json(url):
    with urlopen(url, timeout=5) as response:
        return json.load(response)


def esperar(check, descricao, timeout=60):
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        try:
            if check():
                return
        except (OSError, ValueError):
            pass
        time.sleep(0.5)
    raise RuntimeError("Tempo esgotado: " + descricao)


def demonstracao():
    mensagens = get_json("http://127.0.0.1:8025/api/v1/messages?limit=100")["messages"]
    return [m for m in mensagens if any(
        d.get("Address") in ("ana@example.test", "carla@example.test", "bruno@example.test")
        for d in m.get("To", []))]


def duplicatas():
    codigo = "import sqlite3; c=sqlite3.connect('/data/notificacoes.sqlite3'); print(c.execute(\"SELECT count(*) FROM audit WHERE outcome='duplicate'\").fetchone()[0])"
    return int(compose("exec", "-T", "notificacoes", "python", "-c", codigo))


def main():
    registros = []

    def registrar(nome):
        registros.append({"teste": nome, "passou": True})
        print("PASSOU:", nome, flush=True)

    for porta in (8081, 8082):
        esperar(lambda: get_json(f"http://127.0.0.1:{porta}/ready")["ready"], "serviço pronto")
    registrar("Dois microsserviços prontos")
    esperar(lambda: len(demonstracao()) == 2, "dois lembretes na demonstração")
    emails = demonstracao()
    destinatarios = {d["Address"] for m in emails for d in m["To"]}
    assert destinatarios == {"ana@example.test", "carla@example.test"}, destinatarios
    registrar("Ana e Carla recebem, Bruno não recebe")

    antes = duplicatas()
    compose("exec", "-T", "acompanhamento", "python", "-m", "acompanhamento", "--once")
    esperar(lambda: duplicatas() >= antes + 2, "reprocessamento concluído")
    assert len(demonstracao()) == 2
    registrar("Reprocessamento não gera novos e-mails")

    compose("restart", "notificacoes")
    esperar(lambda: get_json("http://127.0.0.1:8082/ready")["ready"], "consumidor reiniciado")
    antes = duplicatas()
    compose("exec", "-T", "acompanhamento", "python", "-m", "acompanhamento", "--once")
    esperar(lambda: duplicatas() >= antes + 2, "histórico após reinício")
    assert len(demonstracao()) == 2
    registrar("Volume preserva o histórico após reiniciar o consumidor")

    destino = ROOT / "test-results/execucao_containers.json"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(json.dumps({"executado_em": datetime.now(timezone.utc).isoformat(),
        "ambiente": "Docker Compose, dois microsserviços independentes", "casos": registros,
        "passed": len(registros), "failed": 0,
        "docker": subprocess.check_output(["docker", "version", "--format", "{{.Server.Version}}"], text=True).strip(),
        "servicos": compose("ps", "--format", "json")}, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
