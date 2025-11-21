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
        
        simple_commands = [
            "power_on",
            "power_off",
            "volume_up",
            "volume_down",
            "mute",
            "menu",
            "back",
            "exit",
            "home",
            "info",
            "up",
            "down",
            "left",
            "right",
            "enter",
            "channel_up",
            "channel_down",
            "input_next",
            "input_previous",
            "digit_0",
            "digit_1",
            "digit_2",
            "digit_3",
            "digit_4",
            "digit_5",
            "digit_6",
            "digit_7",
            "digit_8",
            "digit_9",
            "function_red",
            "function_green",
            "function_yellow",
            "function_blue",
        ]
        
        super().__init__(
            entity_id,
            entity_name,
            features,
            attributes,
            simple_commands=simple_commands,
            cmd_handler=self.handle_command
        )
        
        self._client.set_notify_callback(self._on_device_update)
        
        _LOG.info(f"Created remote entity: {entity_id}")

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
                _LOG.debug(f"Updated remote attributes for {self.id}")
        
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
        command_map = {
            "power_on": "power_on",
            "power_off": "power_off",
            "volume_up": "volume",
            "volume_down": "volume",
            "mute": "mute",
            "menu": "menu",
            "back": "back",
            "exit": "exit",
            "home": "home",
            "info": "info",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "enter": "enter",
            "channel_up": "channel_up",
            "channel_down": "channel_down",
            "input_next": "input_next",
            "input_previous": "input_previous",
            "digit_0": "digit_0",
            "digit_1": "digit_1",
            "digit_2": "digit_2",
            "digit_3": "digit_3",
            "digit_4": "digit_4",
            "digit_5": "digit_5",
            "digit_6": "digit_6",
            "digit_7": "digit_7",
            "digit_8": "digit_8",
            "digit_9": "digit_9",
            "function_red": "red",
            "function_green": "green",
            "function_yellow": "yellow",
            "function_blue": "blue",
        }
        
        emotiva_cmd = command_map.get(command)
        
        if emotiva_cmd is None:
            _LOG.warning(f"Unknown simple command: {command}")
        elif command == "volume_up":
            await self._client.send_command("volume", "1")
        elif command == "volume_down":
            await self._client.send_command("volume", "-1")
        else:
            await self._client.send_command(emotiva_cmd)