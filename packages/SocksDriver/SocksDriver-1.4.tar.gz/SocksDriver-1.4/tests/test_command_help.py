from socket import gethostname
from SocksDriver import SocksClient


def test_command_help(client: SocksClient) -> None:
    results = client.help()

    assert len(results) == 8

    assert results["blockdev"] == "Return information about block devices on host"
    assert results["help"] == "Get a list of commands"
    assert results["host"] == gethostname()
    assert results["meminfo"] == "Return host memory statistics"
    assert results["sleep"] == "Sleep for a short delay"
    assert results["sysinfo"] == "Return information about the host operating system"
    assert results["uptime"] == "Return time since boot in HH:MM:SS format"
    assert results["version"] == "Return binary version"
