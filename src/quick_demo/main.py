import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from global_state import audio_queue, ws_manager
from worker import ml_worker, metrics_loop



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup Launch background tasks
    ml_task = asyncio.create_task(ml_worker())
    heatbeat_task = asyncio.create_task(ws_manager.heartbeat_loop())
    metrics_task = asyncio.create_task(metrics_loop())
    try:
        yield
    finally:
        # shutdown: cancel and await tasks for cleanup
        ml_task.cancel()
        heatbeat_task.cancel()
        metrics_task.cancel()
        await asyncio.gather(ml_task, heatbeat_task, metrics_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws/transcribe")
async def ws_transcribe(ws: WebSocket):
    conn = await ws_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_bytes()
            if audio_queue.full():
                continue
            await audio_queue.put((conn.cid, data))
    except Exception:
        pass
    finally:
        ws_manager.disconnect(conn.cid)


