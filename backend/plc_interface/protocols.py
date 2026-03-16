from __future__ import annotations

import requests

from backend.config import REST_GATEWAY_BASE_URL
from backend.plc_interface.base import ReadOnlyPLCClient
from backend.plc_interface.mock_data import MOCK_SIGNALS


class MockOPCUAClient(ReadOnlyPLCClient):
    protocol = "opcua"

    def read_signals(self, asset_id: str) -> dict[str, object]:
        return {**MOCK_SIGNALS.get(asset_id, MOCK_SIGNALS["motor-1"]), "protocol": self.protocol}


class MockModbusTCPClient(ReadOnlyPLCClient):
    protocol = "modbus"

    def read_signals(self, asset_id: str) -> dict[str, object]:
        return {**MOCK_SIGNALS.get(asset_id, MOCK_SIGNALS["motor-1"]), "protocol": self.protocol}


class MockMQTTClient(ReadOnlyPLCClient):
    protocol = "mqtt"

    def read_signals(self, asset_id: str) -> dict[str, object]:
        return {**MOCK_SIGNALS.get(asset_id, MOCK_SIGNALS["motor-1"]), "protocol": self.protocol}


class RestGatewayClient(ReadOnlyPLCClient):
    protocol = "rest"

    def read_signals(self, asset_id: str) -> dict[str, object]:
        try:
            response = requests.get(
                f"{REST_GATEWAY_BASE_URL.rstrip('/')}/signals/{asset_id}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return {**data, "protocol": self.protocol}
        except requests.RequestException:
            return {
                **MOCK_SIGNALS.get(asset_id, MOCK_SIGNALS["motor-1"]),
                "protocol": self.protocol,
                "gateway_status": "offline-fallback",
            }


def get_read_only_client(protocol: str) -> ReadOnlyPLCClient:
    normalized = protocol.lower()
    if normalized == "opcua":
        return MockOPCUAClient()
    if normalized == "modbus":
        return MockModbusTCPClient()
    if normalized == "mqtt":
        return MockMQTTClient()
    if normalized == "rest":
        return RestGatewayClient()
    raise ValueError(f"Unsupported protocol: {protocol}. Supported protocols: opcua, modbus, mqtt, rest.")
