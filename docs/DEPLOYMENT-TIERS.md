# EdVirons Edgebox Deployment Tiers

JetKVM is **optional**. Schools can deploy at different tiers based on needs and budget.

---

## Deployment Tiers

### Tier 1: Basic Edgebox (No KVM)
**Cost: ~$200-300**

The standard deployment - no remote BIOS access.

```
┌─────────────────────────────────┐
│         EDGEBOX SERVER          │
│  ┌───────────────────────────┐  │
│  │  Ubuntu + EduCloud Agent  │  │
│  │  + Learning Portal        │  │
│  │  + Admin Dashboard        │  │
│  └───────────────────────────┘  │
│             │                   │
│             ▼                   │
│      School Network → VPN      │
└─────────────────────────────────┘
```

**Remote Capabilities:**
- ✅ SSH access (via VPN)
- ✅ Web admin dashboard
- ✅ Content sync
- ✅ Monitoring & metrics
- ✅ Remote software updates
- ❌ BIOS access
- ❌ OS recovery if boot fails
- ❌ Remote power control

**Best For:**
- Most schools (90%)
- Limited budget
- Stable deployments
- Schools with local IT support

---

### Tier 2: Edgebox + JetKVM
**Cost: ~$310-380**

Full remote management including BIOS-level access.

```
┌─────────────────────────────────┐
│         EDGEBOX SERVER          │
│  ┌───────────────────────────┐  │
│  │  Ubuntu + EduCloud Agent  │  │
│  │  + KVM Agent              │  │
│  └─────────┬─────────────────┘  │
│            │ HDMI + USB         │
│  ┌─────────▼─────────────────┐  │
│  │       JETKVM DEVICE       │  │
│  │  + ATX Extension (opt)    │  │
│  └─────────┬─────────────────┘  │
│            │                    │
│            ▼                    │
│     School Network → VPN       │
└─────────────────────────────────┘
```

**Remote Capabilities:**
- ✅ Everything in Tier 1
- ✅ Remote console (video + keyboard + mouse)
- ✅ BIOS/UEFI setup access
- ✅ Boot menu access
- ✅ OS installation/recovery
- ✅ Power control (with ATX board)
- ✅ Virtual media (ISO mount)

**Best For:**
- Remote/hard-to-reach schools
- Schools with no local IT
- Critical deployments
- Pilot/flagship schools

---

## Feature Comparison

| Feature | Tier 1 (Basic) | Tier 2 (+ KVM) |
|---------|----------------|----------------|
| **Hardware Cost** | $200-300 | $310-380 |
| SSH Access | ✅ | ✅ |
| Web Dashboard | ✅ | ✅ |
| Content Sync | ✅ | ✅ |
| Monitoring | ✅ | ✅ |
| Remote Updates | ✅ | ✅ |
| **Remote Console** | ❌ | ✅ |
| **BIOS Access** | ❌ | ✅ |
| **Power Control** | ❌ | ✅ |
| **OS Recovery** | ❌ | ✅ |
| **ISO Mount** | ❌ | ✅ |
| Local IT Required | Sometimes | No |

---

## Decision Matrix

```
                        ┌─────────────────┐
                        │  New Deployment │
                        └────────┬────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Is school remote/hard   │
                    │ to reach physically?    │
                    └────────────┬────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │                           │
                  YES                          NO
                   │                           │
                   ▼                           ▼
        ┌──────────────────┐      ┌────────────────────┐
        │ Does school have │      │ Budget allows KVM? │
        │ local IT support?│      └─────────┬──────────┘
        └────────┬─────────┘                │
                 │                 ┌────────┴────────┐
        ┌────────┴────────┐        │                 │
        │                 │       YES                NO
       YES                NO       │                 │
        │                 │        ▼                 ▼
        ▼                 ▼   ┌─────────┐      ┌─────────┐
   ┌─────────┐      ┌─────────┐│ TIER 2 │      │ TIER 1 │
   │ TIER 1 │      │ TIER 2 ││ + KVM  │      │ Basic  │
   │ Basic  │      │ + KVM  │└─────────┘      └─────────┘
   └─────────┘      └─────────┘
```

---

## Software Architecture (KVM Optional)

### EduCloud Agent - KVM Detection

```python
# agent.py - KVM is auto-detected

class EduCloudAgent:
    def __init__(self):
        self.kvm_enabled = self.detect_jetkvm()
    
    def detect_jetkvm(self):
        """Check if JetKVM is present on local network"""
        kvm_ip = os.environ.get("JETKVM_HOST", "192.168.1.11")
        try:
            response = requests.get(f"http://{kvm_ip}/api/system/info", timeout=2)
            if response.ok:
                logger.info(f"JetKVM detected at {kvm_ip}")
                return True
        except:
            pass
        logger.info("No JetKVM detected - running in basic mode")
        return False
    
    def get_capabilities(self):
        """Report device capabilities to cloud"""
        caps = {
            "ssh": True,
            "dashboard": True,
            "monitoring": True,
            "sync": True,
        }
        if self.kvm_enabled:
            caps.update({
                "kvm": True,
                "remote_console": True,
                "power_control": True,
                "virtual_media": True,
            })
        return caps
```

### EduCloud Dashboard - Conditional UI

```typescript
// DevicePage.tsx - Show KVM only if enabled

function DeviceActions({ device }) {
  return (
    <div className="actions">
      {/* Always available */}
      <Button onClick={() => openSSH(device)}>SSH</Button>
      <Button onClick={() => openDashboard(device)}>Dashboard</Button>
      <Button onClick={() => syncContent(device)}>Sync</Button>
      
      {/* Only show if KVM enabled */}
      {device.capabilities?.kvm && (
        <>
          <Button onClick={() => openKVM(device)}>🖥️ Remote Console</Button>
          <Button onClick={() => powerAction(device, 'reboot')}>🔄 Reboot</Button>
        </>
      )}
    </div>
  );
}
```

### Database Schema

```sql
-- devices table
CREATE TABLE devices (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    school_id UUID REFERENCES schools(id),
    vpn_ip INET,
    
    -- Capabilities (auto-detected)
    kvm_enabled BOOLEAN DEFAULT FALSE,
    kvm_ip INET,
    atx_enabled BOOLEAN DEFAULT FALSE,
    serial_enabled BOOLEAN DEFAULT FALSE,
    
    -- Status
    status VARCHAR(50),
    last_seen TIMESTAMP,
    capabilities JSONB
);
```

---

## Upgrade Path

Schools can **upgrade from Tier 1 to Tier 2** anytime:

1. **Order JetKVM** ($69) + ATX board ($15)
2. **Ship to school** or deliver during maintenance visit
3. **Local setup** (15 min):
   - Connect HDMI from Edgebox to JetKVM
   - Connect USB from JetKVM to Edgebox
   - Connect ATX board to motherboard headers
   - Connect JetKVM to network
4. **Agent auto-detects** JetKVM on next heartbeat
5. **Dashboard shows** KVM controls automatically

No software changes needed - it's plug and play!

---

## Cost Summary

| Deployment | Hardware | Per School |
|------------|----------|------------|
| 100 schools, Tier 1 only | $200 × 100 | $20,000 |
| 100 schools, 20% with KVM | $200 × 80 + $310 × 20 | $22,200 |
| 100 schools, all with KVM | $310 × 100 | $31,000 |

**Recommendation:** Start with Tier 1, add KVM to remote/critical schools.
