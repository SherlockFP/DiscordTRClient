# yedek plan bu, normalde lazim degil
# olur da goodbyedpi yetmezse diye duruyor
# mantik basit: sen discorda degil bu sunucuya baglaniyorsun,
# sunucu yurtdisindaysa engel islemiyor
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import FileResponse, JSONResponse
import websockets

BASE = Path(__file__).parent
app = FastAPI()

API = "https://discord.com/api/v10"
GATEWAY = "wss://gateway.discord.gg/?v=10&encoding=json"
CDN_OK = ["cdn.discordapp.com", "media.discordapp.net", "images-ext-1.discordapp.net"]

def gonder(path, method, query, body, ctype, auth):
    url = API + "/" + path
    if query:
        url += "?" + query
    h = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    if ctype:
        h["Content-Type"] = ctype
    if auth:
        h["Authorization"] = auth
    data = body if method not in ["GET", "HEAD"] else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read(), r.headers.get_content_type()
    except urllib.error.HTTPError as e:
        return e.code, e.read(), "application/json"

@app.api_route("/relay/rest/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def rest(full_path: str, request: Request):
    # tokeni tutmuyorum, sadece iletiyorum
    auth = request.headers.get("x-discord-auth") or request.headers.get("authorization")
    body = await request.body()
    ctype = request.headers.get("content-type")
    if request.method in ["GET", "HEAD"]:
        body = b""
        ctype = None
    s, d, t = gonder(full_path, request.method, urllib.parse.urlencode(request.query_params), body, ctype, auth)
    return Response(content=d, status_code=s, media_type=t or "application/json")

@app.get("/relay/cdn/{full_path:path}")
async def cdn(full_path: str, request: Request):
    host = request.query_params.get("host", "cdn.discordapp.com")
    if host not in CDN_OK:
        return JSONResponse({"error": "yok"}, status_code=400)
    req = urllib.request.Request("https://" + host + "/" + full_path, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return Response(content=r.read(), media_type=r.headers.get_content_type() or "application/octet-stream")
    except Exception as e:
        return JSONResponse({"error": str(e)[:200]}, status_code=502)

@app.websocket("/relay/gateway")
async def gateway(client_ws: WebSocket):
    await client_ws.accept()
    try:
        async with websockets.connect(GATEWAY, max_size=4 * 1024 * 1024) as d:
            async def gidis():
                try:
                    while True:
                        m = await client_ws.receive_text()
                        await d.send(m)
                except:
                    pass
            async def gelis():
                try:
                    async for m in d:
                        if isinstance(m, bytes):
                            await client_ws.send_bytes(m)
                        else:
                            await client_ws.send_text(m)
                except:
                    pass
            import asyncio
            await asyncio.gather(gidis(), gelis())
    except:
        pass
    try:
        await client_ws.close()
    except:
        pass

@app.get("/")
def index():
    return FileResponse(str(BASE / "index.html"))

@app.get("/health")
def health():
    return {"ok": True}
