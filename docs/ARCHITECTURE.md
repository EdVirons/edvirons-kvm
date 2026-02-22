# EdVirons KVM - Bare Metal Architecture

## Overview

Complete remote management solution for Edgebox servers deployed in schools across Kenya, enabling BIOS-level access, OS recovery, and power control from the central NOC.

---

## 1. Hardware Architecture

### Per-School Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                        SCHOOL SERVER ROOM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      EDGEBOX SERVER                       │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │  Ubuntu Server 22.04 LTS                            │ │   │
│  │  │  - EduCloud Agent                                   │ │   │
│  │  │  - Learning Apps (Kolibri, etc.)                    │ │   │
│  │  │  - Local Admin Dashboard                            │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                           │   │
│  │  Ports:                                                   │   │
│  │  ├─ HDMI Out ──────────────────────┐                     │   │
│  │  ├─ USB (for HID) ─────────────────┼──┐                  │   │
│  │  ├─ ATX Headers ───────────────────┼──┼──┐               │   │
│  │  ├─ Serial (optional) ─────────────┼──┼──┼──┐            │   │
│  │  └─ Ethernet (LAN) ────────────────┼──┼──┼──┼─► School   │   │
│  └────────────────────────────────────┼──┼──┼──┘    Network │   │
│                                       │  │  │               │   │
│  ┌────────────────────────────────────┼──┼──┼────────────┐  │   │
│  │              JETKVM DEVICE         │  │  │            │  │   │
│  │  ┌─────────────────────────────────▼──┼──┼─────────┐  │  │   │
│  │  │  HDMI IN ◄──────────────────────┘  │  │         │  │  │   │
│  │  │  USB HID ◄─────────────────────────┘  │         │  │  │   │
│  │  │                                       │         │  │  │   │
│  │  │  RJ-12 Extension Port ◄───────────────┘         │  │  │   │
│  │  │  (ATX/Serial/DC Power)                          │  │  │   │
│  │  │                                                 │  │  │   │
│  │  │  Ethernet ──────────────────────────────────────┼──┼──┼─► │
│  │  │  (Same network as Edgebox)                      │  │  │   │
│  │  └─────────────────────────────────────────────────┘  │  │   │
│  │                                                       │  │   │
│  │  Extensions:                                          │  │   │
│  │  ├─ ATX Extension Board (power/reset headers)         │  │   │
│  │  ├─ DC Power Control (optional, for 12-20V)           │  │   │
│  │  └─ Serial Console (optional, for RS-232)             │  │   │
│  └───────────────────────────────────────────────────────┘  │   │
│                                                              │   │
└──────────────────────────────────────────────────────────────┘
```

### Hardware Components

| Component | Model | Purpose | Est. Cost |
|-----------|-------|---------|-----------|
| **Edgebox Server** | Mini PC / NUC / RPi 5 | Run learning platform | $150-400 |
| **JetKVM Device** | JetKVM | HDMI capture + USB HID | $69 |
| **ATX Extension** | JetKVM ATX Board | Power/Reset control | $15 |
| **HDMI Cable** | Standard HDMI | Video capture | $5 |
| **USB Cable** | USB-A to USB-C | HID passthrough | $5 |
| **Ethernet** | Cat6 | Network connectivity | $5 |
| **RJ-12 Cable** | 6P6C | Extension connection | Included |

**Total per school: ~$250-500**

---

## 2. Network Architecture

### VPN Topology

```
                                    INTERNET
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
            ▼                           ▼                           ▼
    ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
    │   School A    │          │   School B    │          │   School C    │
    │   Network     │          │   Network     │          │   Network     │
    │               │          │               │          │               │
    │ Edgebox       │          │ Edgebox       │          │ Edgebox       │
    │ 192.168.1.10  │          │ 192.168.1.10  │          │ 192.168.1.10  │
    │               │          │               │          │               │
    │ JetKVM        │          │ JetKVM        │          │ JetKVM        │
    │ 192.168.1.11  │          │ 192.168.1.11  │          │ 192.168.1.11  │
    │               │          │               │          │               │
    │ WireGuard VPN │          │ WireGuard VPN │          │ WireGuard VPN │
    │ 10.10.1.x     │          │ 10.10.2.x     │          │ 10.10.3.x     │
    └───────┬───────┘          └───────┬───────┘          └───────┬───────┘
            │                           │                           │
            └───────────────────────────┼───────────────────────────┘
                                        │
                                        ▼
                            ┌───────────────────────┐
                            │    EDUCLOUD HUB       │
                            │    (Cloud Server)     │
                            │                       │
                            │  WireGuard Server     │
                            │  10.10.0.1            │
                            │                       │
                            │  KVM Proxy            │
                            │  :8090 (WebSocket)    │
                            │                       │
                            │  Web Dashboard        │
                            │  :443 (HTTPS)         │
                            └───────────────────────┘
                                        │
                                        ▼
                            ┌───────────────────────┐
                            │      NOC TEAM         │
                            │   (IT Admins)         │
                            │                       │
                            │  Browser-based KVM    │
                            │  access to any school │
                            └───────────────────────┘
```

### IP Addressing Scheme

| Network | CIDR | Purpose |
|---------|------|---------|
| VPN Hub | 10.10.0.0/24 | Cloud servers |
| School VPN | 10.10.{school_id}.0/24 | Per-school subnet |
| Edgebox | 10.10.{school_id}.10 | Main server |
| JetKVM | 10.10.{school_id}.11 | KVM device |

---

## 3. Software Architecture

### Component Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLOUD LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   EduCloud      │  │   KVM Proxy     │  │   Monitoring    │         │
│  │   Dashboard     │  │   (WebSocket)   │  │   (Grafana)     │         │
│  │                 │  │                 │  │                 │         │
│  │  React + Next   │  │  Python/aiohttp │  │  Prometheus     │         │
│  │  Port 443       │  │  Port 8090      │  │  Port 3000      │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           │                    │                    │                   │
│           └────────────────────┼────────────────────┘                   │
│                                │                                        │
│                    ┌───────────▼───────────┐                           │
│                    │    WireGuard VPN      │                           │
│                    │    Server             │                           │
│                    │    10.10.0.1          │                           │
│                    └───────────┬───────────┘                           │
│                                │                                        │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
                    ═════════════╪═════════════  (Internet / VPN Tunnel)
                                 │
┌────────────────────────────────┼────────────────────────────────────────┐
│                         EDGE LAYER (Per School)                          │
├────────────────────────────────┼────────────────────────────────────────┤
│                                │                                        │
│            ┌───────────────────▼───────────────────┐                   │
│            │           EDGEBOX SERVER              │                   │
│            │                                       │                   │
│            │  ┌─────────────┐  ┌─────────────┐    │                   │
│            │  │  EduCloud   │  │  KVM Agent  │    │                   │
│            │  │  Agent      │  │             │    │                   │
│            │  │             │  │  Connects   │    │                   │
│            │  │  Heartbeat  │  │  to JetKVM  │    │                   │
│            │  │  Sync       │  │  Streams    │    │                   │
│            │  │  Metrics    │  │  to Proxy   │    │                   │
│            │  └─────────────┘  └──────┬──────┘    │                   │
│            │                          │           │                   │
│            │  WireGuard Client ───────┼───────────┼─► VPN to Cloud   │
│            │  10.10.{school}.10       │           │                   │
│            └──────────────────────────┼───────────┘                   │
│                                       │                                │
│            ┌──────────────────────────▼───────────┐                   │
│            │            JETKVM DEVICE             │                   │
│            │                                      │                   │
│            │  ┌────────────────────────────────┐  │                   │
│            │  │  JetKVM Firmware (Linux)       │  │                   │
│            │  │                                │  │                   │
│            │  │  - HDMI Capture (1080p60)      │  │                   │
│            │  │  - H.264 Encoding              │  │                   │
│            │  │  - USB HID Emulation           │  │                   │
│            │  │  - WebRTC/HTTP Streaming       │  │                   │
│            │  │  - ATX Power Control           │  │                   │
│            │  │  - Serial Console (optional)   │  │                   │
│            │  └────────────────────────────────┘  │                   │
│            │                                      │                   │
│            │  REST API: http://192.168.1.11      │                   │
│            │  WebSocket: ws://192.168.1.11/ws    │                   │
│            └──────────────────────────────────────┘                   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        KVM SESSION DATA FLOW                              │
└──────────────────────────────────────────────────────────────────────────┘

1. VIDEO STREAM (Edgebox → Browser)

   Edgebox          JetKVM           KVM Agent        KVM Proxy        Browser
   Display ───HDMI──► Capture ──H.264──► Stream ──WebSocket──► Relay ──► Render
                      1080p60           ~2Mbps        VPN Tunnel        Canvas

2. INPUT (Browser → Edgebox)

   Browser          KVM Proxy        KVM Agent        JetKVM          Edgebox
   Keyboard ──JSON──► Relay ──WebSocket──► Forward ──USB HID──► Input
   Mouse                              VPN Tunnel                      Events

3. POWER CONTROL

   Browser          KVM Proxy        KVM Agent        JetKVM          Edgebox
   Button ───JSON───► Relay ──────────► API Call ──ATX Pins──► Power
   Click                                             RJ-12             On/Off
```

---

## 4. Deployment Topology

### Small School (1 Edgebox)

```
┌────────────────────────────────────────┐
│            COMPUTER LAB                 │
│                                         │
│   ┌─────────┐     ┌─────────┐          │
│   │ Edgebox │────►│ JetKVM  │          │
│   │         │HDMI │         │          │
│   │         │◄────│         │          │
│   │         │USB  │         │          │
│   └────┬────┘     └────┬────┘          │
│        │               │               │
│        └───────┬───────┘               │
│                │ LAN                   │
│        ┌───────▼───────┐               │
│        │    Switch     │               │
│        └───────┬───────┘               │
│                │                       │
│        ┌───────▼───────┐               │
│        │ School Router │──► Internet   │
│        └───────────────┘               │
└────────────────────────────────────────┘
```

### Large School (Multiple Edgeboxes)

```
┌──────────────────────────────────────────────────────────────┐
│                    MULTIPLE COMPUTER LABS                     │
│                                                               │
│   LAB A                    LAB B                    LAB C    │
│  ┌─────────┐              ┌─────────┐              ┌─────────┐│
│  │Edgebox-A│              │Edgebox-B│              │Edgebox-C││
│  │+JetKVM  │              │+JetKVM  │              │+JetKVM  ││
│  └────┬────┘              └────┬────┘              └────┬────┘│
│       │                        │                        │    │
│       └────────────────────────┼────────────────────────┘    │
│                                │                             │
│                        ┌───────▼───────┐                     │
│                        │  Core Switch  │                     │
│                        └───────┬───────┘                     │
│                                │                             │
│                        ┌───────▼───────┐                     │
│                        │ School Router │──► Internet         │
│                        │ (VPN Client)  │                     │
│                        └───────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. JetKVM Integration

### API Endpoints (Local)

```
JetKVM REST API (http://192.168.1.11)

# Video
GET  /api/video/stream         # MJPEG/H.264 stream
GET  /api/video/snapshot       # Single frame capture
POST /api/video/quality        # Set quality (1080p/720p/480p)

# HID (Keyboard/Mouse)
POST /api/hid/keyboard         # Send key event
POST /api/hid/mouse/move       # Move mouse
POST /api/hid/mouse/button     # Mouse click
POST /api/hid/mouse/scroll     # Mouse scroll

# Power (ATX Extension)
GET  /api/atx/state            # Get power/HDD LED state
POST /api/atx/power            # Press power button
POST /api/atx/reset            # Press reset button
POST /api/atx/power/long       # Long-press power (force off)

# Virtual Media
POST /api/media/mount          # Mount ISO/IMG
POST /api/media/eject          # Eject media
GET  /api/media/status         # Get mount status

# Serial Console (Extension)
GET  /api/serial/read          # Read serial output
POST /api/serial/write         # Write to serial
POST /api/serial/config        # Set baud rate, etc.

# System
GET  /api/system/info          # Device info
GET  /api/system/network       # Network config
POST /api/system/reboot        # Reboot JetKVM
```

### KVM Agent ↔ JetKVM Communication

```python
# agent.py - Key interactions

class JetKVMClient:
    def __init__(self, host="192.168.1.11"):
        self.base_url = f"http://{host}"
        self.ws_url = f"ws://{host}/ws"
    
    async def stream_video(self):
        """Stream H.264 video frames"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/video/stream") as resp:
                async for chunk in resp.content.iter_any():
                    yield chunk  # Forward to proxy
    
    async def send_key(self, key, action="press"):
        """Send keyboard input"""
        await self._post("/api/hid/keyboard", {
            "key": key,
            "action": action  # press/down/up
        })
    
    async def power_action(self, action):
        """Control ATX power"""
        endpoints = {
            "on": "/api/atx/power",
            "off": "/api/atx/power",
            "reset": "/api/atx/reset",
            "force-off": "/api/atx/power/long"
        }
        await self._post(endpoints[action])
    
    async def mount_iso(self, url):
        """Mount remote ISO as virtual CD"""
        await self._post("/api/media/mount", {
            "type": "cdrom",
            "url": url
        })
```

---

## 6. Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LAYER 1: VPN Tunnel (WireGuard)                                │
│  ├─ All traffic encrypted (ChaCha20-Poly1305)                   │
│  ├─ Device-specific keys                                        │
│  └─ No direct internet exposure                                 │
│                                                                  │
│  LAYER 2: Proxy Authentication                                  │
│  ├─ Device token (pre-shared)                                   │
│  ├─ JWT for browser sessions                                    │
│  └─ Role-based access (admin/operator/viewer)                   │
│                                                                  │
│  LAYER 3: Action Authorization                                  │
│  ├─ Power actions require elevated role                         │
│  ├─ 2FA for destructive operations (optional)                   │
│  └─ Audit logging for all actions                               │
│                                                                  │
│  LAYER 4: Session Security                                      │
│  ├─ Session timeout (30 min idle)                               │
│  ├─ Single active session per device                            │
│  └─ Force disconnect capability                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Access Roles

| Role | View | Input | Power | Media | Serial | Admin |
|------|------|-------|-------|-------|--------|-------|
| Viewer | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Operator | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Technician | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 7. Cabling Diagram

### Standard Setup

```
                    EDGEBOX SERVER
                    ┌─────────────┐
                    │  ■ ■ ■ ■ ■  │ ◄── Status LEDs
                    │             │
   HDMI ──────────► │  [HDMI]    │
   (to JetKVM)      │             │
                    │  [USB-A]   │ ──► USB to JetKVM (HID)
                    │             │
                    │  [USB-A]   │ ──► Optional peripherals
                    │             │
                    │  [ETH]     │ ──► LAN (Switch)
                    │             │
                    │  [PWR]     │ ◄── DC Power (12-19V)
                    └─────────────┘
                          │
                          │ ATX Headers (inside case)
                          │
    ┌─────────────────────▼─────────────────────┐
    │              ATX EXTENSION                │
    │  ┌─────────────────────────────────────┐  │
    │  │  PWR+  PWR-  RST+  RST-  LED+  LED- │  │
    │  │   │     │     │     │     │     │   │  │
    │  └───┼─────┼─────┼─────┼─────┼─────┼───┘  │
    │      └─────┴─────┴─────┴─────┴─────┘      │
    │              To Motherboard                │
    │                                           │
    │  [RJ-12] ◄─────────────────────────────── │ To JetKVM
    │  [USB-C] ◄─── Power In (optional)        │
    └───────────────────────────────────────────┘


                     JETKVM DEVICE
                    ┌─────────────┐
                    │             │
   From Edgebox ──► │  [HDMI IN] │ Video capture
                    │             │
   To Edgebox ────► │  [USB-C]   │ HID output
                    │             │
   ATX Extension ─► │  [RJ-12]   │ Extension port
                    │             │
   Network ───────► │  [ETH]     │ LAN connection
                    │             │
   Power ─────────► │  [USB-C]   │ 5V power
                    └─────────────┘
```

---

## 8. Bill of Materials (Per School)

### Minimum Setup

| Item | Qty | Unit Cost | Total |
|------|-----|-----------|-------|
| Edgebox Server (Mini PC) | 1 | $200 | $200 |
| JetKVM Device | 1 | $69 | $69 |
| ATX Extension Board | 1 | $15 | $15 |
| HDMI Cable (1.5m) | 1 | $5 | $5 |
| USB-A to USB-C Cable | 1 | $5 | $5 |
| Cat6 Ethernet (2m) | 2 | $3 | $6 |
| USB-C Power Adapter | 1 | $10 | $10 |
| **TOTAL** | | | **$310** |

### Full Setup (with Serial)

| Item | Qty | Unit Cost | Total |
|------|-----|-----------|-------|
| All minimum items | 1 | $310 | $310 |
| Serial Console Extension | 1 | $20 | $20 |
| RS-232 Cable | 1 | $5 | $5 |
| DC Power Extension | 1 | $20 | $20 |
| **TOTAL** | | | **$355** |

---

## 9. Deployment Checklist

### Pre-Installation
- [ ] Verify Edgebox hardware specs
- [ ] Confirm network connectivity
- [ ] Obtain JetKVM device and extensions
- [ ] Prepare cables
- [ ] Generate VPN keys

### Hardware Setup
- [ ] Install Edgebox server
- [ ] Connect HDMI from Edgebox to JetKVM
- [ ] Connect USB from JetKVM to Edgebox
- [ ] Install ATX extension board
- [ ] Connect RJ-12 from ATX board to JetKVM
- [ ] Connect Ethernet cables
- [ ] Power on both devices

### Software Setup
- [ ] Install EduCloud agent on Edgebox
- [ ] Configure WireGuard VPN
- [ ] Install KVM agent
- [ ] Register device in EduCloud dashboard
- [ ] Test video streaming
- [ ] Test keyboard/mouse input
- [ ] Test power controls
- [ ] Test virtual media (if needed)

### Verification
- [ ] Remote console accessible from NOC
- [ ] All power actions working
- [ ] Latency acceptable (<100ms)
- [ ] VPN stable

---

## 10. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No video | HDMI not connected | Check cable, try different port |
| No input | USB not connected | Check USB cable, try different port |
| High latency | Network congestion | Check bandwidth, adjust quality |
| Power not working | ATX not connected | Verify RJ-12 and header connections |
| VPN down | Firewall blocking | Check UDP 51820 allowed |
| Black screen | Edgebox powered off | Use ATX to power on |

### Diagnostic Commands

```bash
# On Edgebox
systemctl status educloud-agent
systemctl status kvm-agent
wg show  # VPN status
ping 10.10.0.1  # Test VPN connectivity

# Test JetKVM
curl http://192.168.1.11/api/system/info
curl http://192.168.1.11/api/atx/state

# On Cloud
docker logs kvm-proxy
```
