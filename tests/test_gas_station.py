from unittest.mock import patch

from fireblocks_sdk import FireblocksSDK


def make_sdk():
    return FireblocksSDK("dummy-private-key", "dummy-api-key")


def test_omits_max_gas_price_when_unset():
    sdk = make_sdk()
    with patch.object(FireblocksSDK, "_put_request", return_value={}) as put:
        sdk.set_gas_station_configuration("100", "1000")
    assert put.call_count == 1
    url, body = put.call_args[0]
    assert url == "/v1/gas_station/configuration"
    assert body == {"gasThreshold": "100", "gasCap": "1000"}


def test_sends_max_gas_price_when_set():
    sdk = make_sdk()
    with patch.object(FireblocksSDK, "_put_request", return_value={}) as put:
        sdk.set_gas_station_configuration("100", "1000", max_gas_price="50")
    body = put.call_args[0][1]
    assert body["maxGasPrice"] == "50"


def test_coerces_int_max_gas_price_to_str():
    sdk = make_sdk()
    with patch.object(FireblocksSDK, "_put_request", return_value={}) as put:
        sdk.set_gas_station_configuration("100", "1000", max_gas_price=50)
    body = put.call_args[0][1]
    assert body["maxGasPrice"] == "50"
