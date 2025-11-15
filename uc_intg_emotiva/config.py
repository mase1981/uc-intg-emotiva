"""
Configuration management for Emotiva integration.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

_LOG = logging.getLogger(__name__)


@dataclass
class DeviceConfig:
    device_id: str
    name: str
    ip_address: str
    model: str
    control_port: int = 7002
    notify_port: int = 7003
    protocol_version: float = 3.0
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "ip_address": self.ip_address,
            "model": self.model,
            "control_port": self.control_port,
            "notify_port": self.notify_port,
            "protocol_version": self.protocol_version,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceConfig":
        return cls(
            device_id=data["device_id"],
            name=data["name"],
            ip_address=data["ip_address"],
            model=data.get("model", "Unknown"),
            control_port=data.get("control_port", 7002),
            notify_port=data.get("notify_port", 7003),
            protocol_version=data.get("protocol_version", 3.0),
            enabled=data.get("enabled", True)
        )


class EmotivaConfig:
    
    def __init__(self, config_file_path: str = "config.json"):
        self._config_file_path = config_file_path
        self._devices: List[DeviceConfig] = []
        self._loaded = False
        
        config_dir = os.path.dirname(self._config_file_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        self._load_config()
    
    def _load_config(self) -> None:
        try:
            if os.path.exists(self._config_file_path):
                with open(self._config_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                devices_data = data.get("devices", [])
                self._devices = [DeviceConfig.from_dict(device_data) for device_data in devices_data]
                
                _LOG.info(f"Loaded configuration with {len(self._devices)} devices")
                self._loaded = True
            else:
                _LOG.info("No existing configuration file found")
                self._devices = []
                self._loaded = True
        except Exception as e:
            _LOG.error(f"Failed to load configuration: {e}")
            self._devices = []
            self._loaded = True
    
    def _save_config(self) -> None:
        try:
            config_data = {
                "devices": [device.to_dict() for device in self._devices],
                "version": "1.0.0"
            }
            
            with open(self._config_file_path, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=2, ensure_ascii=False)
            
            _LOG.info(f"Saved configuration with {len(self._devices)} devices")
        except Exception as e:
            _LOG.error(f"Failed to save configuration: {e}")
            raise
    
    def reload_from_disk(self) -> None:
        _LOG.debug("Reloading configuration from disk")
        self._load_config()
    
    def is_configured(self) -> bool:
        return self._loaded and len(self._devices) > 0
    
    def add_device(self, device: DeviceConfig) -> None:
        existing_ids = [d.device_id for d in self._devices]
        if device.device_id in existing_ids:
            raise ValueError(f"Device ID {device.device_id} already exists")
        
        self._devices.append(device)
        self._save_config()
        _LOG.info(f"Added device: {device.name} ({device.model}) at {device.ip_address}")
    
    def remove_device(self, device_id: str) -> bool:
        original_count = len(self._devices)
        self._devices = [d for d in self._devices if d.device_id != device_id]
        
        if len(self._devices) < original_count:
            self._save_config()
            _LOG.info(f"Removed device: {device_id}")
            return True
        return False
    
    def get_device(self, device_id: str) -> Optional[DeviceConfig]:
        for device in self._devices:
            if device.device_id == device_id:
                return device
        return None
    
    def get_all_devices(self) -> List[DeviceConfig]:
        return self._devices.copy()
    
    def get_enabled_devices(self) -> List[DeviceConfig]:
        return [device for device in self._devices if device.enabled]
    
    def update_device(self, device_id: str, **kwargs) -> bool:
        device = self.get_device(device_id)
        if not device:
            return False
        
        allowed_fields = ['name', 'ip_address', 'model', 'control_port', 'notify_port', 'protocol_version', 'enabled']
        updated = False
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(device, field):
                setattr(device, field, value)
                updated = True
        
        if updated:
            self._save_config()
            _LOG.info(f"Updated device: {device_id}")
        
        return updated
    
    def clear_all_devices(self) -> None:
        self._devices = []
        self._save_config()
        _LOG.info("Cleared all device configurations")
    
    def get_device_count(self) -> int:
        return len(self._devices)
    
    def get_enabled_device_count(self) -> int:
        return len(self.get_enabled_devices())
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_devices": len(self._devices),
            "enabled_devices": len(self.get_enabled_devices()),
            "configured": self.is_configured(),
            "config_file": self._config_file_path
        }
    
    @property
    def config_file_path(self) -> str:
        return self._config_file_path