# EdVirons KVM

Remote KVM (Keyboard, Video, Mouse) solution for managing Edgeboxes and bare-metal servers.

## Features

- 🖥️ **Remote Console** - Full BIOS/OS access via browser
- ⌨️ **Input Passthrough** - Keyboard & mouse over WebSocket
- 📺 **Video Streaming** - Real-time screen capture
- ⚡ **Power Control** - On/Off/Reset/Cycle
- 🔒 **Secure** - Token authentication, VPN-ready

## Architecture

```
Browser ──► KVM Proxy (Cloud) ◄──► KVM Agent ──► JetKVM ──► Edgebox
            Port 8090                            HDMI/USB
```

## Quick Start

### 1. Deploy Proxy (Cloud)

```bash
docker-compose up -d
```

Web Console: http://localhost:8089

### 2. Install Agent (Edgebox)

```bash
export KVM_PROXY_URL="ws://cloud-ip:8090"
export JETKVM_HOST="192.168.1.100"
python3 kvm-agent/agent.py
```

### 3. Connect

Open http://cloud-ip:8089, enter device ID, connect!

## Components

| Component | Description | Port |
|-----------|-------------|------|
| `kvm-proxy/` | WebSocket bridge | 8090 |
| `kvm-agent/` | Edgebox-side agent | - |
| `web-client/` | Browser UI | 8089 |

## Requirements

- JetKVM device connected to Edgebox
- Python 3.8+ with aiohttp
- Docker (for proxy deployment)

## Integration

Works with EduCloud Edgebox management:
- Devices with `jetkvm_enabled=true` show KVM button
- Access via: `/edgeboxes/{id}?tab=kvm`

## License

MIT
