"""Publica un mensaje en un canal de Discord a una hora programada (UTC).

Uso: python publish.py
El script pregunta a qué hora (UTC) publicar, espera hasta ese instante
(adelantándose SEND_LEAD_MS para compensar la latencia de red) y termina
en cuanto el mensaje se ha enviado.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import discord

CONFIG_PATH = Path(__file__).parent / "config.json"
MESSAGE_PATH = Path(__file__).parent / "message.txt"
SEND_LEAD = timedelta(milliseconds=100)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"No se encuentra {CONFIG_PATH.name}. Copia config.example.json a "
            "config.json y rellena token, guild_id y channel_id."
        )
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    for key in ("token", "channel_id"):
        if not config.get(key):
            sys.exit(f"Falta la clave '{key}' en {CONFIG_PATH.name}.")
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


async def wait_until(send_at: datetime) -> None:
    remaining = (send_at - datetime.now(timezone.utc)).total_seconds()
    if remaining > 0:
        print(
            f"Esperando {remaining:.1f}s hasta {send_at.isoformat()} "
            "(UTC, ya incluye el adelanto de 100ms)..."
        )
        await asyncio.sleep(remaining)


async def run() -> None:
    config = load_config()
    content = load_message()
    target = prompt_target_time()
    send_at = target - SEND_LEAD

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        try:
            channel = client.get_channel(config["channel_id"])
            if channel is None:
                channel = await client.fetch_channel(config["channel_id"])

            guild_id = config.get("guild_id")
            channel_guild_id = getattr(getattr(channel, "guild", None), "id", None)
            if guild_id and channel_guild_id and channel_guild_id != guild_id:
                print(
                    "Aviso: el canal indicado no pertenece al guild_id configurado.",
                    file=sys.stderr,
                )

            await wait_until(send_at)
            await channel.send(content)
            print(
                f"Mensaje publicado en #{getattr(channel, 'name', config['channel_id'])} "
                f"a las {datetime.now(timezone.utc).isoformat()} (UTC)."
            )
        except discord.Forbidden:
            sys.exit("El bot no tiene permiso para publicar en ese canal.")
        except discord.NotFound:
            sys.exit("No se encuentra el canal indicado en channel_id.")
        finally:
            await client.close()

    await client.start(config["token"])


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit("\nCancelado por el usuario.")
