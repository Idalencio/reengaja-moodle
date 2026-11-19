"""Republica um evento, preservando a chave. Nunca limpa o histórico de envios."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infra.broker import Broker
from infra.config import Settings
from infra.events import Reminder

parser = argparse.ArgumentParser()
parser.add_argument("arquivo", type=Path, help="JSON do evento v1")
args = parser.parse_args()
event = Reminder.decode(args.arquivo.read_bytes())
with Broker(Settings.load()) as broker:
    broker.publish(event.encode(), event.event_id)
print("Evento republicado:", event.event_id)
