# discod-bot

Script que publica un mensaje en un canal de Discord (vía webhook) a una hora
programada (UTC).

Al ejecutarlo, pregunta a qué hora quieres publicar, espera hasta ese instante
(adelantándose 100ms para compensar la latencia de red) y termina en cuanto
el mensaje se ha enviado.

No usa un bot de Discord: usa un **webhook** de canal, por lo que los mensajes
no llevan la etiqueta "BOT" y se pueden mostrar con el nombre y avatar que tú
elijas (por defecto configurados a tu nombre/foto, para que se parezcan a un
mensaje tuyo). Técnicamente siguen siendo mensajes de webhook, no de tu cuenta
personal: automatizar el envío de mensajes con tu propia cuenta de usuario
("self-bot") está prohibido por los Términos de Servicio de Discord y no está
soportado por este script.

## 1. Crear el webhook en Discord

No hace falta crear ninguna aplicación ni bot. Necesitas permiso de
"Gestionar webhooks" en el servidor:

1. En Discord, entra al canal donde quieres publicar.
2. Editar canal (icono de engranaje) → **Integraciones** → **Webhooks** →
   **Nuevo webhook**.
3. Opcionalmente, ponle nombre/avatar por defecto al webhook (se puede
   sobrescribir por mensaje, ver más abajo).
4. Copia la **URL del webhook** (la necesitarás en `config.json`).

## 2. Configurar

```bash
cp config.example.json config.json
cp message.example.txt message.txt
```

Edita `config.json`:

- `webhook_url`: la URL copiada en el paso anterior.
- `username` (opcional): nombre que aparecerá como remitente del mensaje.
- `avatar_url` (opcional): URL de una imagen para el avatar del mensaje.

Edita `message.txt` con el contenido que quieres publicar. Ambos ficheros
están en `.gitignore` y no se versionan.

## 3. Instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Ejecutar

```bash
python publish.py
```

Introduce la hora en UTC cuando se te solicite, en formato `HH:MM`, `HH:MM:SS`,
o `YYYY-MM-DD HH:MM[:SS]` si es para otro día. El proceso queda esperando y
termina automáticamente tras publicar el mensaje.
