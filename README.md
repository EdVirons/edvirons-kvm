# EdVirons KVM

Remote KVM (Keyboard, Video, Mouse) solution for managing Edgeboxes and bare-metal servers.

## Overview

EdVirons KVM enables remote console access to Edgeboxes, even when the OS is unresponsive or during boot/BIOS operations.

## Features

- 🖥️ Remote console access (pre-boot, BIOS, OS)
- ⌨️ Keyboard/mouse passthrough
- 📺 Video capture & streaming
- ⚡ Power control (on/off/reboot)
- 🔌 Virtual media (ISO mount)
- 🔒 Secure access via VPN

## Architecture

```
┌─────────────┐     VPN      ┌──────────────┐
│  EduCloud   │◄────────────►│   JetKVM     │
│  Dashboard  │              │   Device     │
└─────────────┘              └──────┬───────┘
                                    │ HDMI/USB
                              ┌─────▼─────┐
                              │  Edgebox  │
                              │  Server   │
                              └───────────┘
```

## Components

- `kvm-proxy/` - Cloud-side proxy for KVM connections
- `kvm-agent/` - Agent running alongside JetKVM
- `web-client/` - Browser-based KVM client

## Status

🚧 Under Development
