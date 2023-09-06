import platform
from SocksDriver import SocksClient


def test_command_sysinfo(client: SocksClient) -> None:
    results = client.sysinfo()

    assert len(results) == 6
    assert results["host"] == platform.node()

    assert results["System"] == platform.system()
    assert results["Node"] == platform.node()
    assert results["Release"] == platform.release()
    assert results["Version"] == platform.version()
    assert results["Machine"] == platform.machine()
