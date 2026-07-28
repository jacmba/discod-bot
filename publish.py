"""Publica un mensaje en un canal de Discord (vía webhook) a una hora programada (UTC).

Uso: python publish.py
El script pregunta a qué hora (UTC) publicar, espera hasta ese instante
(adelantándose SEND_LEAD para compensar la latencia de red) y termina en
cuanto el mensaje se ha enviado.
"""

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

CONFIG_PATH = Path(__file__).parent / "config.json"
MESSAGE_PATH = Path(__file__).parent / "message.txt"
SEND_LEAD = timedelta(milliseconds=100)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"No se encuentra {CONFIG_PATH.name}. Copia config.example.json a "
            "config.json y rellena webhook_url."
        )
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if not config.get("webhook_url"):
        sys.exit(f"Falta la clave 'webhook_url' en {CONFIG_PATH.name}.")
    return config


def load_message() -> str:
    if not MESSAGE_PATH.exists():
        sys.exit(
            f"No se encuentra {MESSAGE_PATH.name}. Copia message.example.txt a "
            "message.txt y escribe el mensaje a publicar."
        )
    content = MESSAGE_PATH.read_text(encoding="utf-8").strip()
    if not content:
        sys.exit(f"{MESSAGE_PATH.name} está vacío.")
    return content


def prompt_target_time() -> datetime:
    print("¿A qué hora quieres publicar el mensaje? (UTC)")
    print("Formatos: 'HH:MM[:SS]' (hoy en UTC) o 'YYYY-MM-DD HH:MM[:SS]'")
    raw = input("> ").strip()

    target = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            target = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            break
        except ValueError:
            continue
    if target is None:
        now = datetime.now(timezone.utc)
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                t = datetime.strptime(raw, fmt).time()
                target = datetime.combine(now.date(), t, tzinfo=timezone.utc)
                break
            except ValueError:
                continue
    if target is None:
        sys.exit(f"No se ha podido interpretar la hora '{raw}'.")

    if target - SEND_LEAD <= datetime.now(timezone.utc):
        sys.exit(
            "La hora indicada ya ha pasado (o está demasiado próxima). "
            "Indica una fecha/hora futura; incluye la fecha si es para otro día."
        )
    return target


def wait_until(send_at: datetime) -> None:
    remaining = (send_at - datetime.now(timezone.utc)).total_seconds()
    if remaining > 0:
        print(
            f"Esperando {remaining:.1f}s hasta {send_at.isoformat()} "
            "(UTC, ya incluye el adelanto de 100ms)..."
        )
        time.sleep(remaining)


def send_message(config: dict, content: str) -> None:
    payload = {"content": content}
    if config.get("username"):
        payload["username"] = config["username"]
    if config.get("avatar_url"):
        payload["avatar_url"] = config["avatar_url"]

    response = requests.post(config["webhook_url"], json=payload, timeout=10)
    if response.status_code >= 300:
        sys.exit(f"Error al publicar el mensaje ({response.status_code}): {response.text}")


def main() -> None:
    config = load_config()
    content = load_message()
    target = prompt_target_time()
    send_at = target - SEND_LEAD

    wait_until(send_at)
    send_message(config, content)
    print(f"Mensaje publicado a las {datetime.now(timezone.utc).isoformat()} (UTC).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelado por el usuario.")
