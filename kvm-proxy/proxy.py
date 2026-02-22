#!/usr/bin/env python3
"""
EdVirons KVM Proxy
WebSocket bridge between browser clients and JetKVM devices
"""
import os
import json
import asyncio
import logging
from typing import Dict, Set
from dataclasses import dataclass
from datetime import datetime

from aiohttp import web, WSMsgType
import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Config
PROXY_PORT = int(os.environ.get("PROXY_PORT", "8090"))
AUTH_TOKEN = os.environ.get("KVM_AUTH_TOKEN", "edvirons-kvm-secret")

@dataclass
class KVMDevice:
    device_id: str
    name: str
    ws: web.WebSocketResponse
    connected_at: datetime
    clients: Set[web.WebSocketResponse]

class KVMProxy:
    def __init__(self):
        self.devices: Dict[str, KVMDevice] = {}
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/health", self.health)
        self.app.router.add_get("/api/devices", self.list_devices)
        self.app.router.add_get("/ws/device/{device_id}", self.device_ws)
        self.app.router.add_get("/ws/client/{device_id}", self.client_ws)
    
    async def index(self, request):
        return web.Response(text="EdVirons KVM Proxy v1.0")
    
    async def health(self, request):
        return web.json_response({
            "status": "ok",
            "devices_connected": len(self.devices),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def list_devices(self, request):
        devices = []
        for dev_id, dev in self.devices.items():
            devices.append({
                "device_id": dev_id,
                "name": dev.name,
                "connected_at": dev.connected_at.isoformat(),
                "clients": len(dev.clients)
            })
        return web.json_response({"devices": devices})
    
    async def device_ws(self, request):
        """WebSocket endpoint for KVM devices (JetKVM agents)"""
        device_id = request.match_info["device_id"]
        token = request.query.get("token", "")
        
        if token != AUTH_TOKEN:
            return web.Response(status=403, text="Invalid token")
        
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        device_name = request.query.get("name", f"Device-{device_id[:8]}")
        self.devices[device_id] = KVMDevice(
            device_id=device_id,
            name=device_name,
            ws=ws,
            connected_at=datetime.utcnow(),
            clients=set()
        )
        logger.info(f"Device connected: {device_name} ({device_id})")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.BINARY:
                    # Forward video frames to all clients
                    device = self.devices.get(device_id)
                    if device:
                        for client_ws in device.clients:
                            try:
                                await client_ws.send_bytes(msg.data)
                            except:
                                pass
                elif msg.type == WSMsgType.TEXT:
                    # Handle control messages
                    data = json.loads(msg.data)
                    logger.debug(f"Device message: {data}")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"Device WS error: {ws.exception()}")
        finally:
            if device_id in self.devices:
                del self.devices[device_id]
            logger.info(f"Device disconnected: {device_id}")
        
        return ws
    
    async def client_ws(self, request):
        """WebSocket endpoint for browser clients"""
        device_id = request.match_info["device_id"]
        
        if device_id not in self.devices:
            return web.Response(status=404, text="Device not connected")
        
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        device = self.devices[device_id]
        device.clients.add(ws)
        logger.info(f"Client connected to {device_id}, total clients: {len(device.clients)}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Forward keyboard/mouse input to device
                    try:
                        await device.ws.send_str(msg.data)
                    except:
                        pass
                elif msg.type == WSMsgType.BINARY:
                    try:
                        await device.ws.send_bytes(msg.data)
                    except:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"Client WS error: {ws.exception()}")
        finally:
            device.clients.discard(ws)
            logger.info(f"Client disconnected from {device_id}")
        
        return ws
    
    async def run(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PROXY_PORT)
        await site.start()
        logger.info(f"KVM Proxy running on http://0.0.0.0:{PROXY_PORT}")
        
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    proxy = KVMProxy()
    asyncio.run(proxy.run())
