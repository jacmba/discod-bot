# discod-bot

Script que publica un mensaje en un canal de Discord a una hora programada (UTC).

Al ejecutarlo, pregunta a qué hora quieres publicar, espera hasta ese instante
(adelantándose 100ms para compensar la latencia de red) y termina en cuanto
el mensaje se ha enviado.

## 1. Crear el bot en Discord

1. Ve a https://discord.com/developers/applications y crea una aplicación.
2. En la pestaña **Bot**, crea un bot y copia su **Token** (lo necesitarás en `config.json`).
3. En **OAuth2 > URL Generator**, marca el scope `bot` y el permiso `Send Messages`,
   abre la URL generada e invita el bot a tu servidor.
4. En Discord, activa **Ajustes de usuario > Avanzado > Modo desarrollador** para
   poder copiar los IDs de servidor (guild) y canal con clic derecho > "Copiar ID".

## 2. Configurar

```bash
cp config.example.json config.json
cp message.example.txt message.txt
```

Edita `config.json` con tu token, `guild_id` y `channel_id`. Edita `message.txt`
con el contenido que quieres publicar. Ambos ficheros están en `.gitignore` y
no se versionan.

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
