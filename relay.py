"""
Discord Custom Client - Relay Backend
=====================================
Mantik: TR'deki istemci discord.com / gateway.discord.gg'ye DOGRUDAN
baglanmaz (bu domainler engelli). Sadece bu sunucuya baglanir.
Bu sunucu yurtdisinda (Render EU/US) calistiginda engelsiz oldugu icin
Discord'a forward yapar. Yani GoodbyeDPI gibi sistem geneli driver yok,
sadece Discord trafigi relay'den gecer, internetin geri kalani bozulmaz.

ONEMLI:
- Token sunucuda SAKLANMAZ, loglanmaz. Sadece istek aninda forward edilir.
- User-token ile custom client Discord ToS'a aykiridir, hesap ban riski var.
  Egitim/kisisel kullanim prototipidir. Token'ini kimseyle paylasma.
- v1 sadece TEXT: guild/kanal/mesaj + canli Gateway. Ses/goruntu YOK
  (voice UDP relay bu mimaride mantiksiz/pahali).

Calistir:
  pip install -r requirements.txt
  python -m uvicorn relay:app --port 8090
Render'a atarsan Scord'daki gibi yurtdisi IP'den cikmis olursun.
"""
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import FileResponse, JSONResponse
import websockets

BASE = Path(__file__).parent
app = FastAPI(title="Discord Relay (TR bypass, text-only)")

DISCORD_API = "https://discord.com/api/v10"
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
CDN_HOSTS = ("cdn.discordapp.com", "media.discordapp.net", "images-ext-1.discordapp.net")

HOP_BY_HOP = {"host", "connection", "keep-alive", "transfer-encoding",
              "upgrade", "proxy-authenticate", "te", "trailer"}


def _forward_rest(path: str, method: str, query: str, body: bytes,
                  content_type: Optional[str], auth: Optional[str]):
    url = f"{DISCORD_API}/{path}"
    if query:
        url += f"?{query}"
    headers = {"User-Agent": "DiscordRelay/1.0", "Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    if auth:
        headers["Authorization"] = auth  # "Bot XXX" veya user token; loglama!
    req = urllib.request.Request(url, data=body if method not in ("GET", "HEAD") else None,
                                 headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read(), r.headers.get_content_type()
    except urllib.error.HTTPError as e:
        return e.code, e.read(), "application/json"


@app.api_route("/relay/rest/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def relay_rest(full_path: str, request: Request):
    # Token'i header'dan al, asla diske yazma / loglama.
    auth = request.headers.get("x-discord-auth") or request.headers.get("authorization")
    body = await request.body()
    ctype = request.headers.get("content-type")
    # GET'te bos body gonderme (Discord 400 veriyor)
    if request.method in ("GET", "HEAD"):
        body = b""
        ctype = None
    status, data, ctype_out = _forward_rest(
        full_path, request.method,
        urllib.parse.urlencode(request.query_params),
        body, ctype, auth)
    return Response(content=data, status_code=status, media_type=ctype_out or "application/json")


@app.get("/relay/cdn/{full_path:path}")
async def relay_cdn(full_path: str, request: Request):
    # attachments/proxy/<id>/<hash>/file.png gibi path'ler icin.
    # Hangi CDN host? query ?host= ile gelir, default cdn.discordapp.com
    host = request.query_params.get("host", "cdn.discordapp.com")
    if host not in CDN_HOSTS:
        return JSONResponse({"error": "bad cdn host"}, status_code=400)
    url = f"https://{host}/{full_path}"
    req = urllib.request.Request(url, headers={"User-Agent": "DiscordRelay/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return Response(content=r.read(), media_type=r.headers.get_content_type() or "application/octet-stream")
    except Exception as e:
        return JSONResponse({"error": str(e)[:200]}, status_code=502)


@app.websocket("/relay/gateway")
async def relay_gateway(client_ws: WebSocket):
    """
    Tarayici -> bu sunucu (ws) -> discord gateway (ws).
    TR'den discord.gg'ye direkt baglanti yok, engel islemez.
    """
    await client_ws.accept()
    try:
        async with websockets.connect(GATEWAY_URL, max_size=4 * 1024 * 1024) as discord_ws:
            async def c2d():
                try:
                    while True:
                        msg = await client_ws.receive_text()
                        await discord_ws.send(msg)
                except (WebSocketDisconnect, Exception):
                    pass

            async def d2c():
                try:
                    async for msg in discord_ws:
                        if isinstance(msg, bytes):
                            await client_ws.send_bytes(msg)
                        else:
                            await client_ws.send_text(msg)
                except Exception:
                    pass

            import asyncio
            await asyncio.gather(c2d(), d2c())
    except Exception:
        pass
    finally:
        try:
            await client_ws.close()
        except Exception:
            pass


@app.get("/")
def index():
    return FileResponse(str(BASE / "index.html"))


@app.get("/health")
def health():
    return {"ok": True, "mode": "relay-text-only"}
