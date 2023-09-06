from socket import gethostname
from SocksDriver import SocksClient


def test_command_sleep(client: SocksClient) -> None:
    results = client.sleep()

    assert len(results) == 2
    assert results["host"] == gethostname()
    assert results["outcome"] == "Slept for 1000000 microseconds"
