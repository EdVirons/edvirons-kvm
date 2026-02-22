# EdVirons KVM - Feature Roadmap

Based on JetKVM capabilities + EdVirons-specific needs.

## ✅ Core Features (MVP)

### Video & Control
- [x] 1080p video capture
- [x] H.264 encoding
- [x] Keyboard passthrough
- [x] Mouse passthrough (absolute positioning)
- [x] WebSocket streaming
- [ ] Ultra-low latency (<60ms)
- [ ] 60 FPS streaming
- [ ] WebRTC support (for NAT traversal)

### Power Control
- [x] Basic power actions (on/off/reset)
- [ ] ATX header integration
- [ ] Power LED status
- [ ] HDD LED status
- [ ] Long-press power (force off)
- [ ] Power cycle with delay

## 🚀 Advanced Features

### Virtual Media
- [ ] ISO mounting (virtual CD/DVD)
- [ ] USB flash drive emulation
- [ ] Upload ISO from browser
- [ ] Stream ISO from URL
- [ ] Boot from virtual media

### Serial Console
- [ ] RS-232 serial access
- [ ] Terminal in browser
- [ ] Baud rate configuration
- [ ] Log capture
- [ ] Multiple serial ports

### DC Power Control
- [ ] 12-20V DC power relay
- [ ] Power scheduling
- [ ] Auto-restart on failure
- [ ] Power consumption monitoring

### BIOS/Boot Access
- [ ] BIOS setup access
- [ ] Boot menu (F12)
- [ ] PXE boot trigger
- [ ] Secure boot status

## 🎓 EdVirons-Specific Features

### Multi-Device Management
- [ ] Fleet dashboard (all Edgeboxes)
- [ ] Device groups (by school/region)
- [ ] Bulk power actions
- [ ] Scheduled reboots

### Integration
- [ ] EduCloud dashboard embed
- [ ] VPN auto-discovery
- [ ] Agent health monitoring
- [ ] Alert on device offline

### Security
- [ ] Role-based access (IT admin vs viewer)
- [ ] Session recording
- [ ] Audit logs
- [ ] Two-factor auth for power actions

### Education-Specific
- [ ] Remote OS reinstall (PXE + ISO)
- [ ] Content sync during reboot
- [ ] Wake-on-LAN via cloud
- [ ] Scheduled power-off (save energy)

## Hardware Support

### JetKVM Device
- RJ-12 extension port
- HDMI capture
- USB HID emulation

### Extensions
- ATX Extension Board (motherboard power)
- DC Power Control (12-20V relay)
- Serial Console (RS-232)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     EduCloud Dashboard                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ School A│  │ School B│  │ School C│  │   ...   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
└───────┼────────────┼────────────┼────────────┼──────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌───────────────────────────────────────────────────────────┐
│                      KVM Proxy (Cloud)                     │
│  • WebSocket bridge    • Device registry                  │
│  • WebRTC signaling    • Session management               │
│  • STUN/TURN servers   • Authentication                   │
└───────────────────────────────────────────────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
   [KVM Agent]  [KVM Agent]  [KVM Agent]  [KVM Agent]
        │            │            │            │
        ▼            ▼            ▼            ▼
   [JetKVM]     [JetKVM]     [JetKVM]     [JetKVM]
        │            │            │            │
   HDMI│USB     HDMI│USB     HDMI│USB     HDMI│USB
        ▼            ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │Edgebox │  │Edgebox │  │Edgebox │  │Edgebox │
   └────────┘  └────────┘  └────────┘  └────────┘
```
