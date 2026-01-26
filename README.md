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


## Credits

- **Developer**: Meir Miyara
- **Emotiva**: High-performance video processors
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **Protocol**: Emotiva XML-over-UDP control protocol
- **Community**: Testing and feedback from UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-emotiva/issues)
- **UC Community Forum**: [General discussion and support](https://community.unfoldedcircle.com/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)
- **Emotiva Support**: [Official Emotiva Support](https://emotiva.com/pages/support)

---

**Made with ❤️ for the Unfolded Circle and Emotiva Communities**

**Thank You**: Meir Miyara
