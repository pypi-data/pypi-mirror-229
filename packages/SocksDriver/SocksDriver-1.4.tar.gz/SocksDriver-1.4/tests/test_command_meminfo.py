from socket import gethostname
from psutil import virtual_memory
from SocksDriver import SocksClient


def test_command_meminfo_totalram(client: SocksClient) -> None:
    results = client.meminfo()

    assert len(results) == 2
    assert results["host"] == gethostname()
    assert results["totalram"] == virtual_memory().total
