from pytest import raises, mark
from SocksDriver import SocksClient, errors


@mark.parametrize(
    "addr", ["foobar", "127.0.0.1:8080:", "127.0.0.1:8080:abc", "127.0.0.1::"]
)
def test_handle_invalid_address(addr: str) -> None:
    with raises(errors.SocksConnectionError) as exc:
        SocksClient(addr).connect()

    assert "Address must be of form <ip-addr:port>" in str(exc.value)


@mark.parametrize("addr", [":127.0.0.1", "127.0.0.1:", "127.0.0.1:abc", "127.0.0.1:a2"])
def test_handle_invalid_port(addr: str) -> None:
    with raises(errors.SocksConnectionError) as exc:
        SocksClient(addr).connect()

    assert "Invalid port parsed from address" in str(exc.value)


def test_handle_dead_server() -> None:
    with raises(errors.SocksConnectionError) as exc:
        SocksClient("1.2.3.4:8080").connect()

    assert "Server is possibly dead" in str(exc.value)


def test_handle_connection_refused_error() -> None:
    with raises(errors.SocksConnectionError) as exc:
        SocksClient("127.0.0.1:65000").connect()

    assert "Server is refusing connections on port" in str(exc.value)


def test_send_via_disconnected_client() -> None:
    with raises(errors.SocksTransmissionError) as exc:
        client = SocksClient()
        client.connect()
        client.disconnect()
        client.help()

    assert "Connection to server does not exist" in str(exc.value)
