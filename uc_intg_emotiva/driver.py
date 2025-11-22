"""
Emotiva integration driver for Unfolded Circle Remote.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any

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
setup_state = {"step": "initial", "device_count": 1, "devices_data": []}

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
                
                await client.start_notification_listener()
                
                await client.subscribe_events()
                
                _LOG.info("Detecting capabilities for %s...", device_config.name)
                capabilities = await client.detect_capabilities()
                _LOG.info("Detected %d sources and %d modes for %s", 
                         len(capabilities.get('sources', {})), 
                         len(capabilities.get('modes', [])),
                         device_config.name)

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
                _LOG.info("Successfully setup device: %s with notification listener active", device_config.name)

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
    global config, entities_ready, setup_state

    if isinstance(msg, ucapi.DriverSetupRequest):
        device_count = int(msg.setup_data.get("device_count", 1))
        
        if device_count == 1:
            return await _handle_single_device_setup(msg.setup_data)
        else:
            setup_state = {"step": "collect_ips", "device_count": device_count, "devices_data": []}
            return await _request_device_ips(device_count)
    
    elif isinstance(msg, UserDataResponse):
        if setup_state["step"] == "collect_ips":
            return await _handle_device_ips_collection(msg.input_values)

    return SetupError(IntegrationSetupError.OTHER)


async def _handle_single_device_setup(setup_data: Dict[str, Any]) -> ucapi.SetupAction:
    host = setup_data.get("host", "").strip()
    control_port = int(setup_data.get("control_port", 7002))
    notify_port = int(setup_data.get("notify_port", 7003))
    
    if not host:
        _LOG.error("No host provided")
        return SetupError(IntegrationSetupError.OTHER)
    
    _LOG.info(f"Testing connection to {host}")
    
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


async def _request_device_ips(device_count: int) -> RequestUserInput:
    settings = []
    
    for i in range(device_count):
        settings.extend([
            {
                "id": f"device_{i}_ip",
                "label": {"en": f"Device {i+1} IP Address"},
                "description": {"en": f"IP address for Emotiva processor {i+1} (e.g., 192.168.1.{100+i})"},
                "field": {"text": {"value": f"192.168.1.{100+i}"}}
            },
            {
                "id": f"device_{i}_name", 
                "label": {"en": f"Device {i+1} Name"},
                "description": {"en": f"Friendly name for device {i+1}"},
                "field": {"text": {"value": f"Emotiva Processor {i+1}"}}
            }
        ])
    
    return RequestUserInput(
        title={"en": f"Configure {device_count} Emotiva Processors"},
        settings=settings
    )


async def _handle_device_ips_collection(input_values: Dict[str, Any]) -> ucapi.SetupAction:
    devices_to_test = []
    
    device_index = 0
    while f"device_{device_index}_ip" in input_values:
        ip_input = input_values[f"device_{device_index}_ip"]
        name = input_values[f"device_{device_index}_name"]
        
        devices_to_test.append({
            "host": ip_input.strip(),
            "name": name.strip(),
            "index": device_index
        })
        device_index += 1
    
    _LOG.info(f"Testing connections to {len(devices_to_test)} devices...")
    test_results = await _test_multiple_devices(devices_to_test)
    
    successful_devices = 0
    for device_data, success in zip(devices_to_test, test_results):
        if success:
            device_id = f"emotiva_{device_data['host'].replace('.', '_')}"
            device_config = DeviceConfig(
                device_id=device_id,
                name=device_data['name'],
                ip_address=device_data['host'],
                model="Unknown",
                control_port=7002,
                notify_port=7003,
                protocol_version=3.0
            )
            config.add_device(device_config)
            successful_devices += 1
            _LOG.info(f"✅ Device {device_data['index'] + 1} ({device_data['name']}) connection successful")
        else:
            _LOG.error(f"❌ Device {device_data['index'] + 1} ({device_data['name']}) connection failed")
    
    if successful_devices == 0:
        _LOG.error("No devices could be connected")
        return SetupError(IntegrationSetupError.CONNECTION_REFUSED)
    
    await _initialize_integration()
    _LOG.info(f"Multi-device setup completed: {successful_devices}/{len(devices_to_test)} devices configured")
    return SetupComplete()


async def _test_multiple_devices(devices: List[Dict]) -> List[bool]:
    async def test_device(device_data):
        try:
            device_config = DeviceConfig(
                device_id=f"temp_{device_data['index']}",
                name=device_data['name'],
                ip_address=device_data['host'],
                model="Unknown",
                control_port=7002,
                notify_port=7003
            )
            
            client = EmotivaClient(device_config)
            success = await client.test_connection()
            await client.close()
            
            if success:
                _LOG.info(f"Device {device_data['index'] + 1}: Connection successful")
            return success
        except Exception as e:
            _LOG.error(f"Device {device_data['index'] + 1} test error: {e}")
            return False
    
    tasks = [test_device(device) for device in devices]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [result if isinstance(result, bool) else False for result in results]


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
                _LOG.info(f"Requesting initial state for media player: {entity_id}")
                await media_player._client.update_events([
                    "power", "volume", "source", "mode",
                    "audio_input", "video_input"
                ])
                await asyncio.sleep(0.5)
                await media_player.push_update()
                break
        
        for remote in remotes.values():
            if remote.id == entity_id:
                _LOG.info(f"Requesting initial state for remote: {entity_id}")
                await remote._client.update_events(["power"])
                await asyncio.sleep(0.3)
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