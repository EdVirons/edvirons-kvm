# EdVirons KVM

**Optional** remote KVM (Keyboard, Video, Mouse) add-on for Edgebox deployments.

> ⚠️ **JetKVM is optional!** Most schools work fine with Tier 1 (basic) deployment. Add KVM only for remote/critical schools.

## Deployment Tiers

| Tier | Hardware | Cost | Remote Console | BIOS Access | Power Control |
|------|----------|------|----------------|-------------|---------------|
| **Tier 1: Basic** | Edgebox only | $200-300 | ❌ | ❌ | ❌ |
| **Tier 2: + KVM** | Edgebox + JetKVM | $310-380 | ✅ | ✅ | ✅ |

**Tier 1 still has:** SSH, Web Dashboard, Monitoring, Content Sync, Remote Updates

**Tier 2 adds:** Remote console, BIOS access, OS recovery, Power control, ISO mounting

## When to Use KVM

✅ **Add JetKVM for:**
- Remote/hard-to-reach schools
- Schools with no local IT support
- Critical/pilot deployments
- Frequent OS issues expected

❌ **Skip JetKVM for:**
- Most schools (90%)
- Schools with local IT
- Budget-constrained deployments
- Stable, proven hardware

## Architecture

```
TIER 1 (Basic):                    TIER 2 (+ KVM):
┌─────────────┐                    ┌─────────────┐
│   Edgebox   │                    │   Edgebox   │
│   Server    │                    │   Server    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │ HDMI+USB
       │                           ┌──────▼──────┐
       │                           │   JetKVM    │
       │                           │   Device    │
       │                           └──────┬──────┘
       │                                  │
       ▼                                  ▼
  VPN → Cloud                        VPN → Cloud
  (SSH only)                    (SSH + Remote Console)
```

## Quick Start

### For Tier 2 (KVM-enabled) Schools

**1. Deploy Proxy (Cloud):**
```bash
cd edvirons-kvm
docker-compose up -d
```

**2. Install Agent (Edgebox):**
```bash
export KVM_PROXY_URL="ws://cloud:8090"
export JETKVM_HOST="192.168.1.11"  # JetKVM's IP
python3 kvm-agent/agent.py
```

**3. Connect:** Open http://cloud:8089, enter device ID

## Components

| Component | Description | Required |
|-----------|-------------|----------|
| `kvm-proxy/` | Cloud WebSocket bridge | Only if using KVM |
| `kvm-agent/` | Edgebox-side connector | Only if using KVM |
| `web-client/` | Browser UI | Only if using KVM |

## Auto-Detection

The EduCloud agent **auto-detects** JetKVM:
- If JetKVM found → KVM features enabled
- If not found → Runs in basic mode

No manual configuration needed!

## Hardware (JetKVM)

| Product | Price | Purpose |
|---------|-------|---------|
| [JetKVM Device](https://jetkvm.com) | $69 | HDMI capture + USB HID |
| ATX Extension | $15 | Power/Reset control |
| Serial Extension | $20 | RS-232 console |

## Documentation

- [Deployment Tiers](docs/DEPLOYMENT-TIERS.md) - When to use KVM
- [Architecture](docs/ARCHITECTURE.md) - Full technical design
- [Features](FEATURES.md) - Feature roadmap
- [Quick Start](docs/QUICKSTART.md) - Setup guide

## License

MIT
