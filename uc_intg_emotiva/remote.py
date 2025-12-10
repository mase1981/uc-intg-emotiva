"""
Emotiva Remote entity for Unfolded Circle integration.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from typing import Any

import ucapi
from ucapi import Remote, StatusCodes

from uc_intg_emotiva.client import EmotivaClient
from uc_intg_emotiva.config import DeviceConfig

_LOG = logging.getLogger(__name__)


class EmotivaRemote(Remote):
    
    def __init__(self, client: EmotivaClient, device_config: DeviceConfig, api: ucapi.IntegrationAPI):
        self._client = client
        self._device_config = device_config
        self._api = api
        
        entity_id = f"remote_{device_config.device_id}"
        entity_name = f"{device_config.name} Remote"
        
        features = [
            ucapi.remote.Features.ON_OFF,
            ucapi.remote.Features.TOGGLE,
            ucapi.remote.Features.SEND_CMD,
        ]
        
        attributes = {
            ucapi.remote.Attributes.STATE: ucapi.remote.States.OFF,
        }
        
        simple_commands = self._build_command_list()
        
        super().__init__(
            entity_id,
            entity_name,
            features,
            attributes,
            simple_commands=simple_commands,
            cmd_handler=self.handle_command
        )
        
        self._client.set_notify_callback(self._on_device_update)
        
        _LOG.info(f"Created remote entity: {entity_id} with {len(simple_commands)} commands")

    def _build_command_list(self) -> list:
        commands = [
            "power_on",
            "power_off",
            "volume_up",
            "volume_down",
            "mute",
            "menu",
            "info",
            "up",
            "down",
            "left",
            "right",
            "enter",
            "input_up",
            "input_down",
        ]
        
        detected_sources = self._client.detected_sources
        if detected_sources:
            _LOG.info(f"Adding {len(detected_sources)} source buttons to remote")
            for source_cmd, source_name in detected_sources.items():
                safe_cmd = f"source_{source_name.lower().replace(' ', '_').replace('-', '_')}"
                commands.append(safe_cmd)
                _LOG.debug(f"Added source button: {safe_cmd} -> {source_cmd}")
        else:
            for i in range(1, 9):
                commands.append(f"source_{i}")
        
        detected_modes = self._client.detected_modes
        if detected_modes:
            _LOG.info(f"Adding {len(detected_modes)} mode buttons to remote")
            for mode_name in detected_modes:
                safe_cmd = f"mode_{mode_name.lower().replace(' ', '_').replace('-', '_').replace(':', '')}"
                commands.append(safe_cmd)
                _LOG.debug(f"Added mode button: {safe_cmd}")
        
        trim_channels = self._client.trim_channels
        if trim_channels:
            _LOG.info(f"Adding {len(trim_channels)} trim channels to remote")
            for channel_cmd, channel_name in trim_channels.items():
                up_cmd = f"trim_{channel_cmd}_up"
                down_cmd = f"trim_{channel_cmd}_down"
                commands.append(up_cmd)
                commands.append(down_cmd)
                _LOG.debug(f"Added trim buttons: {up_cmd}, {down_cmd}")
        
        _LOG.info(f"Built command list with {len(commands)} total commands")
        return commands

    def _on_device_update(self):
        _LOG.debug(f"Remote update callback for {self.id}")
        
        try:
            state = ucapi.remote.States.ON if self._client.power else ucapi.remote.States.OFF
            
            new_attributes = {
                ucapi.remote.Attributes.STATE: state,
            }
            
            self.attributes.update(new_attributes)
            
            if self._api and self._api.configured_entities.contains(self.id):
                self._api.configured_entities.update_attributes(self.id, new_attributes)
                _LOG.info(f"Updated remote state: power={self._client.power}")
        
        except Exception as e:
            _LOG.error(f"Error in remote update callback: {e}", exc_info=True)

    async def push_update(self):
        try:
            await self._client.update_events(["power"])
            self._on_device_update()
        except Exception as e:
            _LOG.error(f"Error pushing remote update: {e}")

    async def handle_command(self, entity: ucapi.Entity, cmd_id: str, params: dict[str, Any] | None) -> StatusCodes:
        _LOG.info(f"Remote command: {cmd_id} with params: {params}")
        
        try:
            if cmd_id == ucapi.remote.Commands.ON:
                await self._client.power_on()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.remote.Commands.OFF:
                await self._client.power_off()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.remote.Commands.TOGGLE:
                await self._client.power_toggle()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.remote.Commands.SEND_CMD:
                if params and "command" in params:
                    command = params["command"]
                    delay = params.get("delay", 0)
                    repeat = params.get("repeat", 1)
                    
                    for i in range(repeat):
                        await self._handle_simple_command(command)
                        if i < repeat - 1 and delay > 0:
                            import asyncio
                            await asyncio.sleep(delay / 1000.0)
                    
                    return StatusCodes.OK
                return StatusCodes.BAD_REQUEST
            
            else:
                _LOG.warning(f"Unsupported remote command: {cmd_id}")
                return StatusCodes.NOT_IMPLEMENTED
        
        except Exception as e:
            _LOG.error(f"Error handling remote command {cmd_id}: {e}", exc_info=True)
            return StatusCodes.SERVER_ERROR

    async def _handle_simple_command(self, command: str) -> None:
        if command.startswith("source_"):
            await self._handle_source_command(command)
        elif command.startswith("mode_"):
            await self._handle_mode_command(command)
        elif command.startswith("trim_"):
            await self._handle_trim_command(command)
        else:
            await self._handle_basic_command(command)

    async def _handle_source_command(self, command: str) -> None:
        detected_sources = self._client.detected_sources
        
        if detected_sources:
            for source_cmd, source_name in detected_sources.items():
                safe_cmd = f"source_{source_name.lower().replace(' ', '_').replace('-', '_')}"
                if command == safe_cmd:
                    _LOG.info(f"Switching to source: {source_name} ({source_cmd})")
                    await self._client.set_source_by_command(source_cmd)
                    return
        
        if command in ["source_1", "source_2", "source_3", "source_4", 
                       "source_5", "source_6", "source_7", "source_8"]:
            _LOG.info(f"Direct source selection: {command}")
            await self._client.set_source_by_command(command)
        else:
            _LOG.warning(f"Unknown source command: {command}")

    async def _handle_mode_command(self, command: str) -> None:
        detected_modes = self._client.detected_modes
        
        for mode_name in detected_modes:
            safe_cmd = f"mode_{mode_name.lower().replace(' ', '_').replace('-', '_').replace(':', '')}"
            if command == safe_cmd:
                _LOG.info(f"Setting audio mode: {mode_name}")
                await self._client.set_mode(mode_name)
                return
        
        _LOG.warning(f"Unknown mode command: {command}")

    async def _handle_trim_command(self, command: str) -> None:
        trim_channels = self._client.trim_channels
        
        for channel_cmd, channel_name in trim_channels.items():
            up_cmd = f"trim_{channel_cmd}_up"
            down_cmd = f"trim_{channel_cmd}_down"
            
            if command == up_cmd:
                _LOG.info(f"Trim up: {channel_name}")
                await self._client.trim_up(channel_cmd)
                return
            elif command == down_cmd:
                _LOG.info(f"Trim down: {channel_name}")
                await self._client.trim_down(channel_cmd)
                return
        
        _LOG.warning(f"Unknown trim command: {command}")

    async def _handle_basic_command(self, command: str) -> None:
        command_map = {
            "power_on": "power_on",
            "power_off": "power_off",
            "volume_up": "volume",
            "volume_down": "volume",
            "mute": "mute",
            "menu": "menu",
            "info": "info",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "enter": "enter",
            "input_up": "input_up",
            "input_down": "input_down",
        }
        
        emotiva_cmd = command_map.get(command)
        
        if emotiva_cmd is None:
            _LOG.warning(f"Unknown basic command: {command}")
        elif command == "volume_up":
            await self._client.send_command("volume", "1")
        elif command == "volume_down":
            await self._client.send_command("volume", "-1")
        else:
            await self._client.send_command(emotiva_cmd)