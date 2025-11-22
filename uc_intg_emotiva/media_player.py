"""
Emotiva Media Player entity for Unfolded Circle integration.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from typing import Any

import ucapi
from ucapi import MediaPlayer, StatusCodes

from uc_intg_emotiva.client import EmotivaClient
from uc_intg_emotiva.config import DeviceConfig

_LOG = logging.getLogger(__name__)


class EmotivaMediaPlayer(MediaPlayer):
    
    def __init__(self, client: EmotivaClient, device_config: DeviceConfig, api: ucapi.IntegrationAPI):
        self._client = client
        self._device_config = device_config
        self._api = api
        
        entity_id = f"mp_{device_config.device_id}"
        entity_name = f"{device_config.name} Media Player"
        
        features = [
            ucapi.media_player.Features.ON_OFF,
            ucapi.media_player.Features.TOGGLE,
            ucapi.media_player.Features.VOLUME,
            ucapi.media_player.Features.VOLUME_UP_DOWN,
            ucapi.media_player.Features.MUTE_TOGGLE,
            ucapi.media_player.Features.MUTE,
            ucapi.media_player.Features.UNMUTE,
            ucapi.media_player.Features.SELECT_SOURCE,
            ucapi.media_player.Features.SELECT_SOUND_MODE,
        ]
        
        attributes = {
            ucapi.media_player.Attributes.STATE: ucapi.media_player.States.OFF,
            ucapi.media_player.Attributes.VOLUME: 0,
            ucapi.media_player.Attributes.MUTED: False,
            ucapi.media_player.Attributes.SOURCE: "",
            ucapi.media_player.Attributes.SOURCE_LIST: list(client.sources),
            ucapi.media_player.Attributes.SOUND_MODE: "",
            ucapi.media_player.Attributes.SOUND_MODE_LIST: list(client.available_modes),
        }
        
        options = {
            ucapi.media_player.Options.VOLUME_STEPS: 100
        }
        
        super().__init__(
            entity_id,
            entity_name,
            features,
            attributes,
            device_class=ucapi.media_player.DeviceClasses.RECEIVER,
            options=options,
            cmd_handler=self.handle_command
        )
        
        self._client.set_notify_callback(self._on_device_update)
        
        _LOG.info(f"Created media player entity: {entity_id}")

    def _on_device_update(self):
        _LOG.debug(f"Device update callback for {self.id}")
        
        try:
            state = ucapi.media_player.States.ON if self._client.power else ucapi.media_player.States.OFF
            
            volume_level = self._client.volume_level
            volume = int(volume_level * 100) if volume_level is not None else 0
            
            muted = self._client.mute
            source = self._client.source or ""
            mode = self._client.mode or ""
            
            new_attributes = {
                ucapi.media_player.Attributes.STATE: state,
                ucapi.media_player.Attributes.VOLUME: volume,
                ucapi.media_player.Attributes.MUTED: muted,
                ucapi.media_player.Attributes.SOURCE: source,
                ucapi.media_player.Attributes.SOURCE_LIST: list(self._client.sources),
                ucapi.media_player.Attributes.SOUND_MODE: mode,
                ucapi.media_player.Attributes.SOUND_MODE_LIST: list(self._client.available_modes),
            }
            
            self.attributes.update(new_attributes)
            
            if self._api and self._api.configured_entities.contains(self.id):
                self._api.configured_entities.update_attributes(self.id, new_attributes)
                _LOG.debug(f"Updated attributes for {self.id}: power={self._client.power}, source={source}, mode={mode}")
        
        except Exception as e:
            _LOG.error(f"Error in device update callback: {e}", exc_info=True)

    async def push_update(self):
        try:
            await self._client.update_events(["power", "volume", "source", "mode"])
            self._on_device_update()
        except Exception as e:
            _LOG.error(f"Error pushing update: {e}")

    async def handle_command(self, entity: ucapi.Entity, cmd_id: str, params: dict[str, Any] | None) -> StatusCodes:
        _LOG.info(f"Media player command: {cmd_id} with params: {params}")
        
        try:
            if cmd_id == ucapi.media_player.Commands.ON:
                await self._client.power_on()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.OFF:
                await self._client.power_off()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.TOGGLE:
                await self._client.power_toggle()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.VOLUME:
                if params and "volume" in params:
                    volume_percent = float(params["volume"])
                    volume_level = volume_percent / 100.0
                    actual_volume = (volume_level * self._client._volume_range) + self._client._volume_min
                    await self._client.set_volume(actual_volume)
                    return StatusCodes.OK
                return StatusCodes.BAD_REQUEST
            
            elif cmd_id == ucapi.media_player.Commands.VOLUME_UP:
                await self._client.volume_up()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.VOLUME_DOWN:
                await self._client.volume_down()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.MUTE_TOGGLE:
                await self._client.mute_toggle()
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.MUTE:
                await self._client.set_mute(True)
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.UNMUTE:
                await self._client.set_mute(False)
                return StatusCodes.OK
            
            elif cmd_id == ucapi.media_player.Commands.SELECT_SOURCE:
                if params and "source" in params:
                    source = params["source"]
                    await self._client.set_source(source)
                    return StatusCodes.OK
                return StatusCodes.BAD_REQUEST
            
            elif cmd_id == ucapi.media_player.Commands.SELECT_SOUND_MODE:
                if params and "mode" in params:
                    mode = params["mode"]
                    await self._client.set_mode(mode)
                    return StatusCodes.OK
                return StatusCodes.BAD_REQUEST
            
            else:
                _LOG.warning(f"Unsupported command: {cmd_id}")
                return StatusCodes.NOT_IMPLEMENTED
        
        except Exception as e:
            _LOG.error(f"Error handling command {cmd_id}: {e}", exc_info=True)
            return StatusCodes.SERVER_ERROR