"""
Emotiva integration driver for Unfolded Circle Remote.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
import os
from typing import Dict, List

import ucapi
from ucapi import DeviceStates, Events, StatusCodes, IntegrationSetupError, SetupComplete, SetupError, RequestUserInput, UserDataResponse

from uc_intg_emotiva.client import EmotivaClient
from uc_intg_emotiva.config import EmotivaConfig, DeviceConfig
from uc_intg_emotiva.media_player import EmotivaMediaPlayer
from uc_intg_emotiva.remote import EmotivaRemote

api: ucapi.IntegrationAPI | None = None
config: EmotivaConfig | None = None
clients: Dict[str, EmotivaClient] = {}
media_players: Dict[str, EmotivaMediaPlayer] = {}
remotes: Dict[str, EmotivaRemote] = {}
entities_ready: bool = False
initialization_lock: asyncio.Lock = asyncio.Lock()

_LOG = logging.getLogger(__name__)


async def _initialize_integration():
    global clients, api, config, media_players, remotes, entities_ready
    
    async with initialization_lock:
        if entities_ready:
            _LOG.debug("Entities already initialized, skipping")
            return True
            
        if not config or not config.is_configured():
            _LOG.error("Configuration not found or invalid.")
            if api:
                await api.set_device_state(DeviceStates.ERROR)
            return False

        _LOG.info("Initializing Emotiva integration for %d devices...", len(config.get_all_devices()))
        if api:
            await api.set_device_state(DeviceStates.CONNECTING)

        connected_devices = 0

        api.available_entities.clear()
        clients.clear()
        media_players.clear()
        remotes.clear()

        for device_config in config.get_enabled_devices():
            try:
                _LOG.info("Connecting to Emotiva device: %s at %s", device_config.name, device_config.ip_address)
                
                client = EmotivaClient(device_config)
                
                connection_success = await client.test_connection()
                if not connection_success:
                    _LOG.warning("Failed to connect to device: %s", device_config.name)
                    await client.close()
                    continue

                await client.udp_connect()
                await client.subscribe_events()

                device_name = device_config.name
                device_entity_id = device_config.device_id

                _LOG.info("Connected to Emotiva device: %s (ID: %s, Model: %s)", 
                         device_name, device_entity_id, device_config.model)

                media_player_entity = EmotivaMediaPlayer(client, device_config, api)
                remote_entity = EmotivaRemote(client, device_config, api)

                api.available_entities.add(media_player_entity)
                api.available_entities.add(remote_entity)

                clients[device_config.device_id] = client
                media_players[device_config.device_id] = media_player_entity
                remotes[device_config.device_id] = remote_entity

                connected_devices += 1
                _LOG.info("Successfully setup device: %s", device_config.name)

            except Exception as e:
                _LOG.error("Failed to setup device %s: %s", device_config.name, e, exc_info=True)
                continue

        if connected_devices > 0:
            entities_ready = True
            await api.set_device_state(DeviceStates.CONNECTED)
            _LOG.info("Emotiva integration initialization completed successfully - %d/%d devices connected.", 
                     connected_devices, len(config.get_all_devices()))
            return True
        else:
            entities_ready = False
            if api:
                await api.set_device_state(DeviceStates.ERROR)
            _LOG.error("No devices could be connected during initialization")
            return False


async def setup_handler(msg: ucapi.SetupDriver) -> ucapi.SetupAction:
    global config, entities_ready

    if isinstance(msg, ucapi.DriverSetupRequest):
        setup_mode = msg.setup_data.get("setup_mode", "discover")
        
        if setup_mode == "discover":
            return await _handle_discovery_setup()
        else:
            return await _handle_manual_setup(msg.setup_data)
    
    elif isinstance(msg, UserDataResponse):
        return await _handle_device_selection(msg.input_values)

    return SetupError(IntegrationSetupError.OTHER)


async def _handle_discovery_setup() -> ucapi.SetupAction:
    try:
        _LOG.info("Starting device discovery...")
        discovered_devices = await EmotivaClient.discover(timeout=3)
        
        if not discovered_devices or len(discovered_devices) == 0:
            _LOG.warning("No Emotiva devices discovered")
            return SetupError(IntegrationSetupError.NOT_FOUND)
        
        _LOG.info(f"Discovered {len(discovered_devices)} device(s)")
        
        settings = []
        for idx, (ip, xml_resp) in enumerate(discovered_devices):
            name = "Unknown"
            model = "Unknown"
            control_port = 7002
            notify_port = 7003
            protocol_version = 3.0
            
            try:
                name_elem = xml_resp.find("name")
                if name_elem is not None:
                    name = name_elem.text.strip()
                
                model_elem = xml_resp.find("model")
                if model_elem is not None:
                    model = model_elem.text.strip()
                
                ctrl = xml_resp.find("control")
                if ctrl is not None:
                    version_elem = ctrl.find("version")
                    if version_elem is not None:
                        protocol_version = float(version_elem.text)
                    
                    ctrl_port_elem = ctrl.find("controlPort")
                    if ctrl_port_elem is not None:
                        control_port = int(ctrl_port_elem.text)
                    
                    notify_port_elem = ctrl.find("notifyPort")
                    if notify_port_elem is not None:
                        notify_port = int(notify_port_elem.text)
            
            except Exception as e:
                _LOG.error(f"Error parsing device info: {e}")
            
            settings.append({
                "id": f"device_{idx}_select",
                "label": {"en": f"{name} ({model}) at {ip}"},
                "description": {"en": f"Add this device to your configuration"},
                "field": {
                    "checkbox": {
                        "value": True
                    }
                }
            })
            
            settings.append({
                "id": f"device_{idx}_data",
                "label": {"en": "Device Data"},
                "field": {
                    "text": {
                        "value": f"{ip}|{name}|{model}|{control_port}|{notify_port}|{protocol_version}"
                    }
                }
            })
        
        return RequestUserInput(
            title={"en": f"Select Emotiva Devices ({len(discovered_devices)} found)"},
            settings=settings
        )
        
    except Exception as e:
        _LOG.error(f"Discovery error: {e}", exc_info=True)
        return SetupError(IntegrationSetupError.OTHER)


async def _handle_manual_setup(setup_data: Dict) -> ucapi.SetupAction:
    try:
        host = setup_data.get("host", "").strip()
        control_port = int(setup_data.get("control_port", 7002))
        notify_port = int(setup_data.get("notify_port", 7003))
        
        if not host:
            _LOG.error("No host provided")
            return SetupError(IntegrationSetupError.OTHER)
        
        _LOG.info(f"Testing manual connection to {host}")
        
        device_config = DeviceConfig(
            device_id=f"emotiva_{host.replace('.', '_')}",
            name=f"Emotiva Processor ({host})",
            ip_address=host,
            model="Unknown",
            control_port=control_port,
            notify_port=notify_port,
            protocol_version=3.0
        )
        
        test_client = EmotivaClient(device_config)
        try:
            connection_success = await test_client.test_connection()
        finally:
            await test_client.close()
        
        if not connection_success:
            _LOG.error(f"Connection test failed for {host}")
            return SetupError(IntegrationSetupError.CONNECTION_REFUSED)
        
        config.add_device(device_config)
        await _initialize_integration()
        return SetupComplete()
        
    except Exception as e:
        _LOG.error(f"Manual setup error: {e}", exc_info=True)
        return SetupError(IntegrationSetupError.OTHER)


async def _handle_device_selection(input_values: Dict) -> ucapi.SetupAction:
    try:
        selected_devices = []
        
        device_idx = 0
        while f"device_{device_idx}_select" in input_values:
            selected = input_values.get(f"device_{device_idx}_select", False)
            
            if selected:
                device_data_str = input_values.get(f"device_{device_idx}_data", "")
                parts = device_data_str.split("|")
                
                if len(parts) >= 6:
                    ip = parts[0]
                    name = parts[1]
                    model = parts[2]
                    control_port = int(parts[3])
                    notify_port = int(parts[4])
                    protocol_version = float(parts[5])
                    
                    device_config = DeviceConfig(
                        device_id=f"emotiva_{ip.replace('.', '_')}",
                        name=name,
                        ip_address=ip,
                        model=model,
                        control_port=control_port,
                        notify_port=notify_port,
                        protocol_version=protocol_version
                    )
                    
                    selected_devices.append(device_config)
            
            device_idx += 1
        
        if len(selected_devices) == 0:
            _LOG.error("No devices selected")
            return SetupError(IntegrationSetupError.OTHER)
        
        for device_config in selected_devices:
            config.add_device(device_config)
        
        await _initialize_integration()
        _LOG.info(f"Setup completed with {len(selected_devices)} device(s)")
        return SetupComplete()
        
    except Exception as e:
        _LOG.error(f"Device selection error: {e}", exc_info=True)
        return SetupError(IntegrationSetupError.OTHER)


async def on_subscribe_entities(entity_ids: List[str]):
    _LOG.info("Entities subscribed: %s", entity_ids)
    
    if not entities_ready:
        _LOG.error("RACE CONDITION: Subscription before entities ready!")
        success = await _initialize_integration()
        if not success:
            _LOG.error("Failed to initialize during subscription attempt")
            return
    
    for entity_id in entity_ids:
        for media_player in media_players.values():
            if media_player.id == entity_id:
                await media_player.push_update()
                break
        
        for remote in remotes.values():
            if remote.id == entity_id:
                await remote.push_update()
                break


async def on_connect():
    global entities_ready
    
    _LOG.info("Remote Two connected")
    
    if config:
        config.reload_from_disk()
    
    if config and config.is_configured():
        if not entities_ready:
            _LOG.warning("Entities not ready on connect - initializing now")
            await _initialize_integration()
        else:
            _LOG.info("Entities already ready, confirming connection")
            if api:
                await api.set_device_state(DeviceStates.CONNECTED)
    else:
        _LOG.info("Not configured, waiting for setup")
        if api:
            await api.set_device_state(DeviceStates.DISCONNECTED)


async def on_disconnect():
    _LOG.info("Remote Two disconnected")


async def on_unsubscribe_entities(entity_ids: List[str]):
    _LOG.info("Entities unsubscribed: %s", entity_ids)


async def main():
    global api, config
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    _LOG.info("Starting Emotiva Integration Driver")
    
    try:
        loop = asyncio.get_running_loop()
        
        config_dir = os.getenv("UC_CONFIG_HOME", "./")
        config_file_path = os.path.join(config_dir, "config.json")
        config = EmotivaConfig(config_file_path)

        driver_path = os.path.join(os.path.dirname(__file__), "..", "driver.json")
        api = ucapi.IntegrationAPI(loop)

        if config.is_configured():
            _LOG.info("Pre-configuring entities before UC Remote connection")
            _LOG.info(f"Configuration summary: {config.get_summary()}")
            await _initialize_integration()

        await api.init(os.path.abspath(driver_path), setup_handler)

        api.add_listener(Events.SUBSCRIBE_ENTITIES, on_subscribe_entities)
        api.add_listener(Events.UNSUBSCRIBE_ENTITIES, on_unsubscribe_entities)
        api.add_listener(Events.CONNECT, on_connect)
        api.add_listener(Events.DISCONNECT, on_disconnect)

        if not config.is_configured():
            _LOG.info("Device not configured, waiting for setup...")
            await api.set_device_state(DeviceStates.DISCONNECTED)

        _LOG.info("Emotiva integration driver started successfully")
        await asyncio.Future()
        
    except Exception as e:
        _LOG.critical("Fatal error in main: %s", e, exc_info=True)
    finally:
        _LOG.info("Shutting down Emotiva integration")
        
        for client in clients.values():
            try:
                await client.unsubscribe_events()
                await client.close()
            except Exception as e:
                _LOG.error(f"Error closing client: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOG.info("Integration stopped by user")
    except Exception as e:
        _LOG.error(f"Integration failed: {e}")
        raise
        raise