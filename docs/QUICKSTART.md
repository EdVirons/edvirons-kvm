# EdVirons KVM Quick Start

## Deploy the Proxy (Cloud Side)

```bash
cd edvirons-kvm
docker-compose up -d
```

Access web console: http://localhost:8089

## Setup KVM Agent (Edgebox Side)

On the Edgebox with JetKVM attached:

```bash
pip3 install aiohttp

export KVM_PROXY_URL="ws://YOUR_CLOUD_IP:8090"
export JETKVM_HOST="192.168.1.100"  # JetKVM IP
export DEVICE_ID="your-device-id"
export KVM_AUTH_TOKEN="edvirons-kvm-secret"

python3 kvm-agent/agent.py
```

## Usage

1. Open http://YOUR_CLOUD_IP:8089
2. Enter your device ID
3. Click Connect
4. Use keyboard/mouse as normal
5. ESC to release keyboard capture

## Power Actions

- Power On/Off/Reset via toolbar
- Ctrl+Alt+Del for login screens
