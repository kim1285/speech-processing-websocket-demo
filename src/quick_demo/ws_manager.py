from fastapi import WebSocket
from typing import Dict
import asyncio


class WSConnection:
    def __init__(self, cid: str, ws: WebSocket):
        self.cid = cid
        self.ws = ws
        self.last_pong = asyncio.get_event_loop().time()

    async def send(self, payload: dict):
        await self.ws.send_json(payload)


class WSConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WSConnection] = {}
        self.on_disconnect = None  # Callback for cleanup

    async def connect(self, ws: WebSocket) -> WSConnection:
        await ws.accept()
        cid = str(id(ws))
        conn = WSConnection(cid, ws)
        self.connections[cid] = conn
        return conn

    def disconnect(self, cid: str):
        if cid in self.connections:
            del self.connections[cid]
        if self.on_disconnect:
            self.on_disconnect(cid)

    def get(self, cid: str) -> WSConnection | None:
        return self.connections.get(cid)

    async def heartbeat_loop(self):
        while True:
            to_disconnect = []
            now = asyncio.get_event_loop().time()
            for cid, conn in list(self.connections.items()):
                if now - conn.last_pong > 30:  # Dead if no pong in 30s
                    to_disconnect.append(cid)
                else:
                    try:
                        await conn.ws.send_ping()
                    except:
                        to_disconnect.append(cid)
            for cid in to_disconnect:
                self.disconnect(cid)
            await asyncio.sleep(10)  # Check every 10s