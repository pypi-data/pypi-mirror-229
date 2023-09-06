from SocksDriver import SocksClient


def test_is_not_connected() -> None:
    client = SocksClient()
    assert not client.connected


def test_is_connected_after_connect() -> None:
    client = SocksClient()
    assert not client.connected

    client.connect()
    assert client.connected


def test_is_not_connected_after_disconnect() -> None:
    client = SocksClient()
    assert not client.connected

    client.connect()
    assert client.connected

    client.disconnect()
    assert not client.connected
