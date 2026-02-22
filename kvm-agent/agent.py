#!/usr/bin/env python3
"""
EdVirons KVM Agent
Connects JetKVM to cloud proxy, handles video capture & input relay
"""
import os
import json
import asyncio
import logging
import subprocess
from datetime import datetime

import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Config
PROXY_URL = os.environ.get("KVM_PROXY_URL", "ws://localhost:8090")
DEVICE_ID = os.environ.get("DEVICE_ID", "")
DEVICE_NAME = os.environ.get("DEVICE_NAME", "Edgebox-KVM")
AUTH_TOKEN = os.environ.get("KVM_AUTH_TOKEN", "edvirons-kvm-secret")
JETKVM_HOST = os.environ.get("JETKVM_HOST", "192.168.1.100")
JETKVM_API = os.environ.get("JETKVM_API", f"http://{JETKVM_HOST}")

class KVMAgent:
    def __init__(self):
        self.device_id = DEVICE_ID or self.get_device_id()
        self.session = None
        self.proxy_ws = None
        self.running = True
    
    def get_device_id(self):
        """Generate device ID from machine-id"""
        try:
            with open("/etc/machine-id") as f:
                return f.read().strip()[:16]
        except:
            import uuid
            return str(uuid.uuid4())[:16]
    
    async def connect_proxy(self):
        """Connect to cloud KVM proxy"""
        url = f"{PROXY_URL}/ws/device/{self.device_id}?token={AUTH_TOKEN}&name={DEVICE_NAME}"
        
        while self.running:
            try:
                async with self.session.ws_connect(url) as ws:
                    self.proxy_ws = ws
                    logger.info(f"Connected to proxy: {PROXY_URL}")
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self.handle_input(json.loads(msg.data))
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WS error: {ws.exception()}")
                            break
            except Exception as e:
                logger.warning(f"Proxy connection failed: {e}")
            
            logger.info("Reconnecting in 5s...")
            await asyncio.sleep(5)
    
    async def handle_input(self, data):
        """Handle keyboard/mouse input from client"""
        input_type = data.get("type")
        
        try:
            if input_type == "keydown":
                await self.send_key(data.get("key"), press=True)
            elif input_type == "keyup":
                await self.send_key(data.get("key"), press=False)
            elif input_type == "mousemove":
                await self.send_mouse_move(data.get("x"), data.get("y"))
            elif input_type == "mousedown":
                await self.send_mouse_click(data.get("button"), press=True)
            elif input_type == "mouseup":
                await self.send_mouse_click(data.get("button"), press=False)
            elif input_type == "power":
                await self.power_action(data.get("action"))
        except Exception as e:
            logger.error(f"Input handling error: {e}")
    
    async def send_key(self, key, press=True):
        """Send keyboard input to JetKVM"""
        action = "keydown" if press else "keyup"
        async with self.session.post(f"{JETKVM_API}/api/hid/keyboard", json={
            "action": action,
            "key": key
        }) as resp:
            pass
    
    async def send_mouse_move(self, x, y):
        """Send mouse movement to JetKVM"""
        async with self.session.post(f"{JETKVM_API}/api/hid/mouse/move", json={
            "x": x, "y": y, "absolute": True
        }) as resp:
            pass
    
    async def send_mouse_click(self, button, press=True):
        """Send mouse click to JetKVM"""
        action = "mousedown" if press else "mouseup"
        async with self.session.post(f"{JETKVM_API}/api/hid/mouse/button", json={
            "action": action,
            "button": button
        }) as resp:
            pass
    
    async def power_action(self, action):
        """Execute power action via JetKVM"""
        logger.info(f"Power action: {action}")
        async with self.session.post(f"{JETKVM_API}/api/power/{action}") as resp:
            return await resp.json()
    
    async def stream_video(self):
        """Capture video from JetKVM and send to proxy"""
        while self.running:
            try:
                async with self.session.get(f"{JETKVM_API}/api/video/stream") as resp:
                    async for chunk in resp.content.iter_any():
                        if self.proxy_ws and not self.proxy_ws.closed:
                            await self.proxy_ws.send_bytes(chunk)
            except Exception as e:
                logger.warning(f"Video stream error: {e}")
            
            await asyncio.sleep(1)
    
    async def run(self):
        """Main agent loop"""
        logger.info(f"Starting KVM Agent")
        logger.info(f"Device ID: {self.device_id}")
        logger.info(f"JetKVM: {JETKVM_API}")
        
        self.session = aiohttp.ClientSession()
        
        try:
            await asyncio.gather(
                self.connect_proxy(),
                self.stream_video(),
            )
        finally:
            await self.session.close()

if __name__ == "__main__":
    agent = KVMAgent()
    asyncio.run(agent.run())
