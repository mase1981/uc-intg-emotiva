# Emotiva Processor Integration for Unfolded Circle Remote 2/3

Control your Emotiva video processors (XMC-1, XMC-2, RMC-1, RMC-1L) directly from your Unfolded Circle Remote 2 or Remote 3 with comprehensive media player and remote control functionality, **complete surround sound mode selection**, **source switching**, and **full volume control**.

![Emotiva](https://img.shields.io/badge/Emotiva-Video%20Processor-red)
[![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-emotiva?style=flat-square)](https://github.com/mase1981/uc-intg-emotiva/releases)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/mase1981/uc-intg-emotiva?style=flat-square)](https://github.com/mase1981/uc-intg-emotiva/issues)
[![Community Forum](https://img.shields.io/badge/community-forum-blue?style=flat-square)](https://community.unfoldedcircle.com/)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-emotiva/total?style=flat-square)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg?style=flat-square)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA&style=flat-square)](https://github.com/sponsors/mase1981)


## Features

This integration provides comprehensive control of Emotiva video processors through the Emotiva XML-over-UDP protocol, delivering seamless integration with your Unfolded Circle Remote for complete home theater control.

---
## 💰 Support Development

If you find this integration useful, consider supporting development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)

Your support helps maintain this integration. Thank you! ❤️
---

### 🎵 **Media Player Control**

#### **Power Management**
- **Power On/Off** - Complete power control
- **Power Toggle** - Quick power state switching
- **State Feedback** - Real-time power state monitoring

#### **Volume Control**
- **Volume Up/Down** - Precise volume adjustment
- **Set Volume** - Direct volume control (-96dB to +11dB)
- **Volume Slider** - Visual volume control (0-100 scale)
- **Mute Toggle** - Quick mute/unmute
- **Unmute** - Explicit unmute control

#### **Source Selection**
Control all available input sources:
- **HDMI Inputs** - HDMI 1-8 selection
- **Analog Inputs** - Analog 1-5, Analog 7.1
- **Digital Inputs** - Coax 1-4, Optical 1-4
- **ARC Input** - HDMI ARC support
- **Other Sources** - Tuner, USB Stream

#### **Sound Mode Selection**
Access all supported surround sound modes:
- **Stereo** - Pure 2-channel audio
- **Direct** - Bypass processing mode
- **Dolby** - Dolby Digital/Dolby Atmos
- **DTS** - DTS/DTS Neural:X
- **All Stereo** - Stereo to all speakers
- **Auto** - Automatic mode selection
- **Reference Stereo** - Reference quality stereo
- **Surround** - Multi-channel surround

### 🎛️ **Remote Control Entity**

Each processor gets a dedicated remote control with:
- **Power Controls** - On, Off, Toggle
- **Volume Controls** - Up, Down, Mute
- **Navigation** - Cursor Up/Down/Left/Right, Enter
- **Menu Controls** - Menu, Back, Home, Info
- **Channel Controls** - Channel Up/Down
- **Numeric Input** - Digits 0-9
- **Function Buttons** - Red, Green, Yellow, Blue color buttons

### 🔌 **Multi-Device Support**

- **Multiple Processors** - Control unlimited Emotiva processors on your network
- **Individual Configuration** - Each processor gets media player + remote control entity
- **Auto-Discovery** - Automatic detection via UDP broadcast
- **Manual Configuration** - Direct IP address entry as fallback
- **Model Detection** - Automatic model identification (XMC-1, XMC-2, RMC-1, RMC-1L)

### **Supported Models**

#### **XMC-1** - 11-Channel Processor
- Full surround sound mode support
- 8 HDMI inputs with 4K/60Hz support
- Analog and digital inputs
- Dirac Live room correction ready

#### **XMC-2** - 16-Channel Processor  
- Dolby Atmos and DTS:X support
- 8 HDMI inputs with 4K/60Hz HDR
- Advanced surround modes including Dolby Surround
- Enhanced processing capabilities

#### **RMC-1** - Reference Processor
- Dolby Atmos and DTS:X support
- Premium 16-channel processing
- Dirac Live room correction
- Advanced video processing

#### **RMC-1L** - Reference Processor (Lite)
- Dolby Atmos and DTS:X support
- 13-channel processing
- Same features as RMC-1 with reduced channel count

### **Protocol Requirements**

- **Protocol**: Emotiva XML-over-UDP (Version 3.0)
- **Control Port**: 7002 (UDP)
- **Notification Port**: 7003 (UDP)
- **Discovery Port**: 7000 (broadcast request) / 7001 (response)
- **Network Access**: Processor must be on same local network
- **Firewall**: UDP ports 7000-7003 must be accessible

### **Network Requirements**

- **Local Network Access** - Integration requires same network as Emotiva processor
- **UDP Protocol** - Firewall must allow UDP traffic on ports 7000-7003
- **Broadcast Support** - Network must support UDP broadcast for auto-discovery
- **Static IP Recommended** - Processor should have static IP or DHCP reservation

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mase1981/uc-intg-emotiva/releases) page
2. Download the latest `uc-intg-emotiva-<version>.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### Option 2: Docker (Advanced Users)

The integration is available as a pre-built Docker image from GitHub Container Registry:

**Image**: `ghcr.io/mase1981/uc-intg-emotiva:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-emotiva:
    image: ghcr.io/mase1981/uc-intg-emotiva:latest
    container_name: uc-intg-emotiva
    network_mode: host
    volumes:
      - </local/path>:/data
    environment:
      - UC_CONFIG_HOME=/data
      - UC_INTEGRATION_HTTP_PORT=9090
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name=uc-intg-emotiva --network host -v </local/path>:/data -e UC_CONFIG_HOME=/data -e UC_INTEGRATION_HTTP_PORT=9090 --restart unless-stopped ghcr.io/mase1981/uc-intg-emotiva:latest
```

## Configuration

### Step 1: Prepare Your Emotiva Processor

**IMPORTANT**: Emotiva processor must be powered on and connected to your network before adding the integration.

#### Verify Network Connection:
1. Check that processor is connected to network (Ethernet recommended)
2. Note the IP address from processor's network settings
3. Ensure processor firmware is up to date
4. Verify UDP control is enabled (default)

#### Network Setup:
- **Wired Connection**: Recommended for stability
- **Static IP**: Recommended via DHCP reservation
- **Firewall**: Allow UDP ports 7000-7003
- **Network Isolation**: Must be on same subnet as Remote

### Step 2: Setup Integration

1. After installation, go to **Settings** → **Integrations**
2. The Emotiva integration should appear in **Available Integrations**
3. Click **"Configure"** and select setup mode:

#### **Auto-Discovery Mode (Recommended):**

   **Discovery Phase:**
   - Integration broadcasts UDP discovery request
   - All Emotiva processors on network respond
   - Review list of discovered processors
   - Each shows: Name, Model, IP Address
   
   **Selection Phase:**
   - Select which processors to add (checkboxes)
   - Multiple processors supported
   - Click **Complete Setup**

#### **Manual Configuration Mode:**

   **Manual Entry:**
   - **IP Address**: Enter processor IP (e.g., 192.168.1.118)
   - **Control Port**: Default 7002 (change only if customized)
   - **Notification Port**: Default 7003 (change only if customized)
   - Click **Complete Setup**
   
   **Connection Test:**
   - Integration verifies processor connectivity
   - Model information retrieved automatically
   - Setup fails if processor unreachable

4. Integration will create **TWO entities per processor**:
   - **Media Player**: `media_player.emotiva_[ip]` - Full playback control
   - **Remote Control**: `remote.emotiva_[ip]` - Remote functionality

## Using the Integration

### Media Player Entity

The media player entity provides complete processor control:

- **Power Control**: On/Off/Toggle with state feedback
- **Volume Control**: Volume slider (-96dB to +11dB mapped to 0-100)
- **Volume Buttons**: Up/Down with real-time feedback
- **Mute Control**: Toggle, Mute, Unmute
- **Source Selection**: Dropdown with all available inputs
- **Sound Mode**: Dropdown with model-specific surround modes
- **State Display**: Current power, volume, source, and mode

### Remote Control Entity

The remote control entity provides traditional remote functionality:

#### **Available Commands:**
- **Power**: power_on, power_off, power_toggle
- **Volume**: volume_up, volume_down, mute
- **Navigation**: cursor_up, cursor_down, cursor_left, cursor_right, cursor_enter
- **Menu**: menu, back, home, info
- **Channels**: channel_up, channel_down
- **Numbers**: digit_0 through digit_9
- **Functions**: function_red, function_green, function_yellow, function_blue

#### **Remote Features:**
- **Repeat**: Send commands multiple times
- **Delay**: Add delay between repeated commands
- **State Sync**: Power state reflected in remote status

## Troubleshooting

### Processor Not Discovered

**Symptoms**: Auto-discovery finds no devices

**Solutions:**
1. **Verify Processor Power**: Ensure processor is fully powered on
2. **Check Network**: Confirm processor and Remote on same subnet
3. **Firewall Rules**: Allow UDP broadcast on ports 7000-7001
4. **Manual Entry**: Use manual configuration with processor IP
5. **Network Tools**: Use `ping [processor-ip]` to verify connectivity

### Entities Show "Unavailable"

**Symptoms**: Entities appear but show unavailable status

**Solutions:**
1. **Check Network**: Verify processor is reachable
2. **Verify Ports**: Ensure UDP 7002-7003 are accessible
3. **Restart Integration**: Disable and re-enable integration
4. **Check Logs**: Review integration logs for connection errors
5. **Reconfigure**: Remove and re-add integration

### Commands Not Working

**Symptoms**: Commands sent but processor doesn't respond

**Solutions:**
1. **Verify Control Port**: Confirm port 7002 is correct
2. **Check Processor State**: Ensure processor is powered on
3. **Network Congestion**: Verify network has sufficient bandwidth
4. **Firmware Version**: Update processor firmware if outdated
5. **Protocol Support**: Confirm processor supports XML-over-UDP control

### Volume Control Issues

**Symptoms**: Volume changes but display incorrect

**Solutions:**
1. **Volume Range**: Integration uses -96dB to +11dB scale
2. **Scaling**: 0-100 on Remote maps to full processor range
3. **Refresh State**: Request status update via integration
4. **Check Calibration**: Verify processor volume calibration

### Sound Mode Not Changing

**Symptoms**: Mode command sent but no change

**Solutions:**
1. **Model Compatibility**: Verify mode supported by your model
2. **Input Signal**: Some modes require specific input signals
3. **Mode Availability**: Check processor display for available modes
4. **Firmware**: Update processor firmware for mode support

### Log Analysis

**Integration Logs:**
```bash
# Web Interface
Settings → Integrations → Emotiva → View Logs

# Docker Logs
docker logs uc-intg-emotiva
```

**Common Log Messages:**
- `Discovery complete: found X device(s)` - Discovery successful
- `Connection test successful` - Processor reachable
- `UDP connection established` - Communication active
- `Subscribed to events` - Receiving processor notifications
- `Cannot connect UDP socket` - Network/firewall issue

### Known Limitations

- **Firmware Dependent**: Some features require specific firmware versions
- **Network Latency**: UDP protocol sensitive to network delays
- **Broadcast Discovery**: May not work across VLANs
- **Single Zone**: Zone 2 control not currently implemented
- **Model Variations**: Some modes vary by processor model

## Advanced Configuration

### Custom Port Configuration

Edit `config.json` in integration data directory:

```json
{
  "devices": [
    {
      "device_id": "emotiva_192_168_1_118",
      "name": "Emotiva Processor (192.168.1.118)",
      "ip_address": "192.168.1.118",
      "model": "XMC-2",
      "control_port": 7002,
      "notify_port": 7003,
      "protocol_version": 3.0,
      "enabled": true
    }
  ],
  "version": "1.0.0"
}
```

- **control_port**: UDP control port (default: 7002)
- **notify_port**: UDP notification port (default: 7003)
- **protocol_version**: Protocol version (default: 3.0)
- **enabled**: Enable/disable specific device

### Multiple Processors

The integration supports **unlimited Emotiva processors** on your network:

1. **Discovery**: All processors discovered automatically
2. **Selection**: Choose which to add during setup
3. **Individual Control**: Each processor gets separate entities
4. **Independent State**: Each maintains own state and configuration

### Firewall Configuration

**Required UDP Ports:**
- **7000**: Discovery requests (broadcast)
- **7001**: Discovery responses
- **7002**: Control commands
- **7003**: Status notifications

**Windows Firewall:**
```powershell
New-NetFirewallRule -DisplayName "Emotiva Discovery" -Direction Inbound -Protocol UDP -LocalPort 7000-7001 -Action Allow
New-NetFirewallRule -DisplayName "Emotiva Control" -Direction Inbound -Protocol UDP -LocalPort 7002-7003 -Action Allow
```

**Linux (ufw):**
```bash
sudo ufw allow 7000:7003/udp
```

## For Developers

### Local Development

1. **Clone and setup:**
   ```bash
   git clone https://github.com/mase1981/uc-intg-emotiva.git
   cd uc-intg-emotiva
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration:**
   ```bash
   export UC_CONFIG_HOME=./config
   ```

3. **Run development:**
   ```bash
   python uc_intg_emotiva/driver.py
   ```

4. **VS Code debugging:**
   - Open project in VS Code
   - Use F5 to start debugging session
   - Configure integration with real Emotiva processor

### Project Structure

```
uc-intg-emotiva/
├── uc_intg_emotiva/          # Main package
│   ├── __init__.py           # Package info
│   ├── client.py             # Emotiva XML-over-UDP client
│   ├── config.py             # Configuration management
│   ├── driver.py             # Main integration driver
│   ├── media_player.py       # Media player entity
│   └── remote.py             # Remote control entity
├── .github/workflows/        # GitHub Actions CI/CD
│   └── build.yml             # Automated build pipeline
├── docker-compose.yml        # Docker deployment
├── Dockerfile                # Container build instructions
├── driver.json               # Integration metadata
├── requirements.txt          # Dependencies
├── pyproject.toml            # Python project config
└── README.md                 # This file
```

### Key Implementation Details

#### **Emotiva XML-over-UDP Protocol**
- Uses UDP for all communication (no TCP)
- XML format with specific header encoding
- Port 7002 for control commands
- Port 7003 for asynchronous notifications
- Protocol version 3.0 support

#### **Command Format**
```xml
<?xml version="1.0" encoding="utf-8"?>
<emotivaControl protocol="3.0">
  <power_on ack="no"/>
</emotivaControl>
```

#### **Notification Subscription**
```xml
<?xml version="1.0" encoding="utf-8"?>
<emotivaSubscription protocol="3.0">
  <power/>
  <volume/>
  <source/>
  <mode/>
</emotivaSubscription>
```

#### **Multi-Device Architecture**
- Each processor = separate client instance
- Independent UDP connections per device
- Separate media_player + remote entities
- Device ID = `emotiva_{ip_with_underscores}`

#### **Sound Mode Mapping**
```python
# Model-specific mode availability
XMC_1_MODES = ["Stereo", "Direct", "Dolby", "DTS", "All Stereo", ...]
XMC_2_MODES = [..., "Dolby ATMOS", "dts Neural:X", ...]
RMC_1_MODES = [..., "Dolby Surround", "Dolby ATMOS", ...]
```

#### **Volume Scaling**
- Processor range: -96dB to +11dB (107 steps)
- Remote range: 0-100 (percentage)
- Formula: `volume_percent = (db_value + 96) / 107 * 100`
- Mute state tracked separately

#### **Reboot Survival Pattern**
```python
# Pre-initialize entities if config exists
if config.is_configured():
    await _initialize_integration()

# Reload config on reconnect
async def on_connect():
    config.reload_from_disk()
    if not entities_ready:
        await _initialize_integration()
```

### Emotiva Protocol Reference

Essential XML commands used by this integration:

```xml
<!-- Discovery -->
<emotivaPing protocol="3.0"/>

<!-- Power Control -->
<emotivaControl protocol="3.0">
  <power_on ack="no"/>
  <power_off ack="no"/>
</emotivaControl>

<!-- Volume Control -->
<emotivaControl protocol="3.0">
  <volume value="1" ack="no"/>        <!-- Up -->
  <volume value="-1" ack="no"/>       <!-- Down -->
  <set_volume value="-20" ack="no"/>  <!-- Set to -20dB -->
  <mute ack="no"/>                     <!-- Toggle -->
</emotivaControl>

<!-- Source Selection -->
<emotivaControl protocol="3.0">
  <source_1 ack="no"/>  <!-- Input 1 -->
  <hdmi1 ack="no"/>     <!-- HDMI 1 -->
  <analog1 ack="no"/>   <!-- Analog 1 -->
</emotivaControl>

<!-- Mode Selection -->
<emotivaControl protocol="3.0">
  <mode_stereo ack="no"/>
  <mode_dolby ack="no"/>
  <mode_auto ack="no"/>
</emotivaControl>

<!-- Status Request -->
<emotivaUpdate protocol="3.0">
  <power/>
  <volume/>
  <source/>
  <mode/>
</emotivaUpdate>

<!-- Event Subscription -->
<emotivaSubscription protocol="3.0">
  <power/>
  <volume/>
  <source/>
  <mode/>
  <audio_input/>
  <video_input/>
</emotivaSubscription>
```

### Testing Protocol

#### **Discovery Testing**
```python
# Test auto-discovery
devices = await EmotivaClient.discover(timeout=3)
assert len(devices) > 0
```

#### **Connection Testing**
```python
# Test control port connectivity
client = EmotivaClient(device_config)
success = await client.test_connection()
assert success is True
```

#### **Command Testing**
```python
# Test power control
await client.power_on()
await asyncio.sleep(1)
assert client.power is True
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test with real Emotiva processor
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style

- Follow PEP 8 Python conventions
- Use type hints for all functions
- Async/await for all I/O operations
- Comprehensive docstrings
- Descriptive variable names
- Header comments only (no inline comments)

## Credits

- **Developer**: Meir Miyara
- **Emotiva**: High-performance home theater processors
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **Protocol**: Emotiva XML-over-UDP control protocol
- **Community**: Testing and feedback from UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-emotiva/issues)
- **UC Community Forum**: [General discussion and support](https://community.unfoldedcircle.com/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)
- **Emotiva Support**: [Official Emotiva Forums](https://emotiva.com/community/)

---

**Made with ❤️ for the Unfolded Circle and Emotiva Communities** 

**Thank You**: Meir Miyara