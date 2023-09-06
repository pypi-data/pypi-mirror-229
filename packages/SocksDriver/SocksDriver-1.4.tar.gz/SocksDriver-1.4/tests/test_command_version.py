from socket import gethostname
from SocksDriver import SocksClient


def test_command_version(client: SocksClient) -> None:
    results = client.version()

    assert "version" in results
    assert results["host"] == gethostname()
