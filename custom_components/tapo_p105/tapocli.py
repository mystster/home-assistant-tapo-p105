"""tapo cli wrapper."""

import json
import logging
from pathlib import Path
import subprocess

from homeassistant import exceptions

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class TapoCli:
    """tapo cli wrapper."""

    def __init__(self, config_path: str, ip: str, username: str, password: str) -> None:
        """Initialize for wrapper."""
        self._tapocli = str(
            Path(config_path) / "custom_components" / DOMAIN / "bin" / "tapo2"
        )
        self._ip = ip
        self._username = username
        self._password = password

    def _exec_tapocli(self, arg: str) -> str:
        try:
            res = subprocess.run(
                args=[self._tapocli, self._ip, self._username, self._password, arg],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        except subprocess.TimeoutExpired as e:
            # can not connect to device
            raise InvalidIpError from e
        if res.stderr != "":
            _LOGGER.info("tapo2 stderr:%s", res.stderr)
            if res.stderr.find("Login failed") >= 0:
                raise AuthError
            if res.stderr.find("tapo2.h") >= 0:
                raise CannotConnectError
            raise UnknownError
        _LOGGER.info("tapo2 stdout:%s", res.stdout)
        return res.stdout

    def info(self) -> any:
        """Get device info."""
        res = ""
        exec_count = 0
        while res == "" and exec_count < 5:
            exec_count += 1
            res = self._exec_tapocli("info")
        try:
            j = json.loads(res)
        except json.JSONDecodeError as j:
            raise InvalidResponseError from j
        else:
            return json.loads(res)

    def on(self):
        """Device on."""
        self._exec_tapocli("on")

    def off(self):
        """Device off."""
        self._exec_tapocli("off")

    def isOn(self) -> bool:
        """Is device is on."""
        res = self.info
        return res["device_on"]


class CannotConnectError(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidIpError(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""


class InvalidResponseError(exceptions.HomeAssistantError):
    """Error to indicate response is not valid json."""


class AuthError(exceptions.HomeAssistantError):
    """Error to indicate cannot auth."""


class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate unknown error."""
