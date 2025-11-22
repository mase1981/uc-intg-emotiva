"""
Emotiva Device Client Implementation

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
import socket
import time
from typing import Any, Callable, Dict, Optional, List
from lxml import etree

from uc_intg_emotiva.config import DeviceConfig

_LOG = logging.getLogger(__name__)


class EmotivaClient:
    XML_HEADER = '<?xml version="1.0" encoding="utf-8"?>'.encode("utf-8")
    DISCOVER_REQ_PORT = 7000
    DISCOVER_RESP_PORT = 7001

    def __init__(self, device_config: DeviceConfig):
        self._device_config = device_config
        self._ip = device_config.ip_address
        self._control_port = device_config.control_port
        self._notify_port = device_config.notify_port
        self._protocol_version = device_config.protocol_version
        self._name = device_config.name
        self._model = device_config.model
        
        self._udp_stream = None
        self._notify_callback: Optional[Callable] = None
        self._current_state: Dict[str, Any] = {}
        
        self._volume_max = 11
        self._volume_min = -80
        self._volume_range = self._volume_max - self._volume_min
        self._muted = False
        
        self._modes = self._get_sound_modes_for_model(self._model)
        self._sources = self._get_available_sources()
        self._detected_sources: Dict[str, str] = {}
        self._detected_modes: List[str] = []
        
        self._notify_events = {
            "power", "zone2_power", "source", "mode", "volume",
            "audio_input", "audio_bits", "audio_bitstream",
            "video_input", "video_format", "video_space"
        }
        
        for i in range(1, 9):
            self._notify_events.add(f"input_{i}")
        
        self._all_events = {
            "power", "source", "dim", "mode", "speaker_preset",
            "center", "subwoofer", "surround", "back", "volume",
            "loudness", "treble", "bass", "zone2_power", "zone2_volume",
            "zone2_input", "tuner_band", "tuner_channel", "tuner_signal",
            "tuner_program", "tuner_RDS", "audio_input", "audio_bitstream",
            "audio_bits", "video_input", "video_format", "video_space"
        }
        
        for i in range(1, 9):
            self._all_events.add(f"input_{i}")
        
        for ev in self._notify_events:
            self._current_state[ev] = None

    def _get_sound_modes_for_model(self, model: str) -> Dict[str, list]:
        stripped_model = model.replace(" ", "").replace("-", "").replace("_", "").upper()[:4]
        
        if stripped_model == "XMC1":
            return {
                "Stereo": ["stereo", "mode_stereo", False],
                "Direct": ["direct", "mode_direct", False],
                "Dolby": ["dolby", "mode_dolby", False],
                "DTS": ["dts", "mode_dts", False],
                "All Stereo": ["all_stereo", "mode_all_stereo", False],
                "Auto": ["auto", "mode_auto", False],
                "Reference Stereo": ["reference_stereo", "mode_ref_stereo", False],
                "Surround": ["surround_mode", "mode_surround", False],
                "PLIIx Music": ["dolby", "mode_dolby", False],
                "PLIIx Movie": ["dolby", "mode_dolby", False],
                "dts Neo:6 Cinema": ["dts", "mode_dts", False],
                "dts Neo:6 Music": ["dts", "mode_dts", False],
            }
        elif stripped_model == "XMC2":
            return {
                "Stereo": ["stereo", "mode_stereo", False],
                "Direct": ["direct", "mode_direct", False],
                "Dolby": ["dolby", "mode_dolby", False],
                "DTS": ["dts", "mode_dts", False],
                "All Stereo": ["all_stereo", "mode_all_stereo", False],
                "Auto": ["auto", "mode_auto", False],
                "Reference Stereo": ["reference_stereo", "mode_ref_stereo", False],
                "Surround": ["surround_mode", "mode_surround", False],
                "Dolby ATMOS": ["dolby", "mode_dolby", False],
                "dts Neural:X": ["dts", "mode_dts", False],
                "Dolby Surround": ["dolby", "mode_dolby", False],
            }
        elif stripped_model in ["RMC1", "RMC1L"]:
            return {
                "Stereo": ["stereo", "mode_stereo", False],
                "Direct": ["direct", "mode_direct", False],
                "Dolby": ["dolby", "mode_dolby", False],
                "DTS": ["dts", "mode_dts", False],
                "All Stereo": ["all_stereo", "mode_all_stereo", False],
                "Auto": ["auto", "mode_auto", False],
                "Reference Stereo": ["reference_stereo", "mode_ref_stereo", False],
                "Surround": ["surround_mode", "mode_surround", False],
                "Dolby Surround": ["dolby", "mode_dolby", False],
                "Dolby ATMOS": ["dolby", "mode_dolby", False],
                "dts Neural:X": ["dts", "mode_dts", False],
            }
        else:
            return {
                "Stereo": ["stereo", "mode_stereo", False],
                "Direct": ["direct", "mode_direct", False],
                "Dolby": ["dolby", "mode_dolby", False],
                "DTS": ["dts", "mode_dts", False],
                "All Stereo": ["all_stereo", "mode_all_stereo", False],
                "Auto": ["auto", "mode_auto", False],
                "Reference Stereo": ["reference_stereo", "mode_ref_stereo", False],
                "Surround": ["surround_mode", "mode_surround", False],
            }

    def _get_available_sources(self) -> Dict[str, str]:
        return {
            "source_1": "Input 1", "source_2": "Input 2", "source_3": "Input 3",
            "source_4": "Input 4", "source_5": "Input 5", "source_6": "Input 6",
            "source_7": "Input 7", "source_8": "Input 8",
            "analog1": "Analog 1", "analog2": "Analog 2", "analog3": "Analog 3",
            "analog4": "Record In", "analog5": "Analog 5", "analog71": "Analog 7.1",
            "ARC": "HDMI ARC",
            "coax1": "Coax 1", "coax2": "Coax 2", "coax3": "Coax 3", "coax4": "AES/EBU",
            "hdmi1": "HDMI 1", "hdmi2": "HDMI 2", "hdmi3": "HDMI 3", "hdmi4": "HDMI 4",
            "hdmi5": "HDMI 5", "hdmi6": "HDMI 6", "hdmi7": "HDMI 7", "hdmi8": "HDMI 8",
            "optical1": "Optical 1", "optical2": "Optical 2", "optical3": "Optical 3", "optical4": "Optical 4",
            "source_tuner": "Tuner", "usb_stream": "USB Stream",
        }

    @classmethod
    async def discover(cls, timeout: int = 3) -> list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(("", 0))
        except Exception as e:
            _LOG.error(f"Cannot create discovery socket: {e}")
            return []
        
        sock.settimeout(0.5)
        
        req = cls.format_request("emotivaPing", {}, {"protocol": "3.0"})
        
        _LOG.debug("Sending discovery broadcast to port %d", cls.DISCOVER_REQ_PORT)
        
        try:
            sock.sendto(req, ("<broadcast>", cls.DISCOVER_REQ_PORT))
            sock.sendto(req, ("255.255.255.255", cls.DISCOVER_REQ_PORT))
        except Exception as e:
            _LOG.error(f"Failed to send discovery broadcast: {e}")
            sock.close()
            return []
        
        devices = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                resp_data, (ip, port) = sock.recvfrom(4096)
                resp = cls._parse_response(resp_data)
                _LOG.info(f"Discovery response from {ip}:{port}")
                
                device_exists = any(d[0] == ip for d in devices)
                if not device_exists:
                    devices.append((ip, resp))
                    _LOG.debug(f"Added device at {ip}")
            except socket.timeout:
                continue
            except Exception as e:
                _LOG.debug(f"Discovery receive error: {e}")
                continue
        
        sock.close()
        _LOG.info(f"Discovery complete: found {len(devices)} device(s)")
        
        return devices

    async def detect_capabilities(self) -> Dict[str, Any]:
        _LOG.info(f"Detecting capabilities for {self._name}")
        
        capabilities = {
            "sources": {},
            "modes": [],
            "has_tuner": False,
            "max_inputs": 8,
        }
        
        try:
            await self.udp_connect()
            
            for i in range(1, 9):
                await self.update_events([f"input_{i}"])
            
            await self.update_events(["mode"])
            
            await asyncio.sleep(2.0)
            
            for i in range(1, 9):
                input_key = f"input_{i}"
                if input_key in self._current_state and self._current_state[input_key]:
                    input_name = self._current_state[input_key]
                    if input_name and input_name.strip():
                        source_cmd = f"source_{i}"
                        capabilities["sources"][source_cmd] = input_name
                        self._detected_sources[source_cmd] = input_name
                        _LOG.debug(f"Detected source: {source_cmd} = {input_name}")
            
            for mode_name, mode_data in self._modes.items():
                if mode_data[2]:
                    capabilities["modes"].append(mode_name)
                    self._detected_modes.append(mode_name)
                    _LOG.debug(f"Detected mode: {mode_name}")
            
            _LOG.info(f"Capability detection complete: {len(capabilities['sources'])} sources, {len(capabilities['modes'])} modes")
            
        except Exception as e:
            _LOG.error(f"Error detecting capabilities: {e}")
        
        return capabilities

    async def test_connection(self) -> bool:
        try:
            _LOG.info(f"Testing connection to {self._name} at {self._ip}")
            await self.udp_connect()
            
            msg = self.format_request(
                "emotivaUpdate",
                [("power", {})],
                {"protocol": "3.0"} if self._protocol_version == 3 else {}
            )
            
            await self._udp_send(msg)
            await asyncio.sleep(0.5)
            
            await self.udp_disconnect()
            _LOG.info(f"Connection test successful for {self._name}")
            return True
        except Exception as e:
            _LOG.error(f"Connection test failed for {self._name}: {e}")
            return False

    async def udp_connect(self):
        try:
            import asyncio_datagram
            self._udp_stream = await asyncio_datagram.connect((self._ip, self._control_port))
            _LOG.debug(f"UDP connection established to {self._ip}:{self._control_port}")
        except Exception as e:
            _LOG.error(f"Cannot connect UDP socket: {e}")
            raise

    async def udp_disconnect(self):
        try:
            if self._udp_stream:
                self._udp_stream.close()
                self._udp_stream = None
                _LOG.debug(f"UDP connection closed for {self._ip}")
        except Exception as e:
            _LOG.error(f"Cannot disconnect UDP socket: {e}")

    async def _udp_send(self, req):
        try:
            if self._udp_stream:
                await self._udp_stream.send(req)
        except Exception as e:
            _LOG.error(f"Error sending UDP request: {e}")
            try:
                _LOG.debug("Reconnecting UDP stream...")
                await self.udp_connect()
                if self._udp_stream:
                    await self._udp_stream.send(req)
            except Exception as reconnect_error:
                _LOG.error(f"Reconnection failed: {reconnect_error}")

    async def subscribe_events(self):
        _LOG.debug(f"Subscribing to events: {self._notify_events}")
        msg = self.format_request(
            "emotivaSubscription",
            [(ev, None) for ev in self._notify_events],
            {"protocol": "3.0"} if self._protocol_version == 3.0 else {}
        )
        await self._udp_send(msg)

    async def unsubscribe_events(self):
        _LOG.debug(f"Unsubscribing from events: {self._all_events}")
        msg = self.format_request(
            "emotivaUnsubscribe",
            [(ev, None) for ev in self._all_events],
            {"protocol": "3.0"} if self._protocol_version == 3.0 else {}
        )
        await self._udp_send(msg)
        await asyncio.sleep(0.5)

    async def update_events(self, events):
        msg = self.format_request(
            "emotivaUpdate",
            [(ev, {}) for ev in events],
            {"protocol": "3.0"} if self._protocol_version == 3 else {}
        )
        await self._udp_send(msg)

    async def send_command(self, command: str, value: str = "0"):
        msg = self.format_request(
            "emotivaControl",
            [(command, {"value": str(value), "ack": "no"})],
            {"protocol": "3.0"} if self._protocol_version == 3 else {}
        )
        await self._udp_send(msg)

    async def power_on(self):
        await self.send_command("power_on")

    async def power_off(self):
        await self.send_command("power_off")

    async def power_toggle(self):
        if self.power:
            await self.power_off()
        else:
            await self.power_on()

    async def volume_up(self):
        await self.send_command("volume", "1")

    async def volume_down(self):
        await self.send_command("volume", "-1")

    async def set_volume(self, vol: float):
        await self.send_command("set_volume", str(vol))

    async def mute_toggle(self):
        await self.send_command("mute")

    async def set_mute(self, enable: bool):
        mute_cmd = "mute_on" if enable else "mute_off"
        await self.send_command(mute_cmd)

    async def set_source(self, source: str):
        source_key = None
        for key, value in self._sources.items():
            if value == source:
                source_key = key
                break
        
        if source_key:
            await self.send_command(source_key)
        else:
            _LOG.error(f"Source '{source}' not found")

    async def set_source_by_command(self, source_command: str):
        await self.send_command(source_command)

    async def set_mode(self, mode: str):
        if mode not in self._modes:
            _LOG.error(f"Mode '{mode}' not found")
            return
        
        mode_cmd = self._modes[mode][0]
        if not mode_cmd:
            _LOG.error(f"Mode '{mode}' has no command")
            return
        
        await self.send_command(mode_cmd)
        
        if "Music" in mode or "music" in mode.lower():
            await asyncio.sleep(0.25)
            await self.send_command("music")
        elif "Movie" in mode or "Cinema" in mode or "cinema" in mode.lower():
            await asyncio.sleep(0.25)
            await self.send_command("movie")

    async def set_mode_by_command(self, mode_command: str):
        await self.send_command(mode_command)

    async def input_next(self):
        await self.send_command("input_up")
    
    async def input_previous(self):
        await self.send_command("input_down")

    def set_notify_callback(self, callback: Callable):
        self._notify_callback = callback

    def handle_notification(self, data: bytes):
        decoded_data = data.decode("utf-8")
        if "emotivaUnsubscribe" not in decoded_data:
            resp = self._parse_response(data)
            self._handle_status(resp)
            
            if self._notify_callback:
                self._notify_callback()

    def _handle_status(self, resp):
        _LOG.debug("Handling status update")
        for elem in resp:
            if elem.tag == "property":
                elem.tag = elem.get("name")
            
            if elem.tag not in self._current_state and not elem.tag.startswith("mode_"):
                continue
            
            val = (elem.get("value") or "").strip()
            visible = (elem.get("visible") or "").strip()
            
            if elem.tag.startswith("mode_"):
                for mode_name, mode_data in self._modes.items():
                    if mode_data[1] == elem.tag:
                        mode_data[2] = True if visible == "true" else False
                        self._modes[mode_name] = mode_data
            
            if elem.tag.startswith("input_") and visible != "true":
                continue
            
            if elem.tag == "volume":
                if val == "Mute":
                    self._muted = True
                    continue
                self._muted = False
            
            if val:
                self._current_state[elem.tag] = val
            
            if elem.tag.startswith("input_"):
                num = elem.tag[6:]
                source_key = f"source_{num}"
                self._sources[source_key] = val
                if val and val.strip():
                    self._detected_sources[source_key] = val

    @classmethod
    def _parse_response(cls, data):
        try:
            parser = etree.XMLParser(ns_clean=True, recover=True)
            root = etree.XML(data, parser)
        except etree.ParseError as e:
            _LOG.error(f"XML parse error: {e}")
            return etree.Element("empty")
        return root

    @classmethod
    def format_request(cls, pkt_type, req, pkt_attrs=None):
        if pkt_attrs is None:
            pkt_attrs = {}
        output = cls.XML_HEADER
        builder = etree.TreeBuilder()
        builder.start(pkt_type, pkt_attrs)
        for cmd, params in req:
            builder.start(cmd, params if params else {})
            builder.end(cmd)
        builder.end(pkt_type)
        pkt = builder.close()
        return output + etree.tostring(pkt)

    @property
    def name(self):
        return self._name

    @property
    def model(self):
        return self._model

    @property
    def ip_address(self):
        return self._ip

    @property
    def power(self):
        return self._current_state.get("power") == "On"

    @property
    def volume(self):
        if self._current_state.get("volume"):
            return float(self._current_state["volume"].replace(" ", ""))
        return None

    @property
    def volume_level(self):
        if self.volume is not None:
            return (self.volume - self._volume_min) / self._volume_range
        return None

    @property
    def mute(self):
        return self._muted

    @property
    def source(self):
        return self._current_state.get("source")

    @property
    def sources(self):
        return tuple(self._sources.values())

    @property
    def detected_sources(self):
        return self._detected_sources

    @property
    def mode(self):
        return self._current_state.get("mode", "")

    @property
    def available_modes(self):
        return tuple(mode for mode, data in self._modes.items() if data[2])

    @property
    def detected_modes(self):
        return self._detected_modes

    @property
    def current_state(self):
        return self._current_state

    async def close(self):
        await self.udp_disconnect()