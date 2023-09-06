from datetime import timedelta
from pathlib import Path
from socket import gethostname
from SocksDriver import SocksClient


def test_command_uptime(client: SocksClient) -> None:
    results = client.uptime()

    proc_results = Path("/proc/uptime").read_text()
    uptime_sec = float(proc_results.split()[0])

    uptime_hh_mm_ss_msec = str(timedelta(seconds=uptime_sec))
    uptime_hh_mm_ss = uptime_hh_mm_ss_msec.split(".", maxsplit=1)[0]

    assert len(results) == 2
    assert uptime_hh_mm_ss in results["uptime"]
    assert results["host"] == gethostname()
