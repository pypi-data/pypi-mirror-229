from typing import TypedDict

TYPE_BLOCKDEV = TypedDict(
    "TYPE_BLOCKDEV",
    {
        "avail_blocks": int,
        "avail_size": int,
        "block_size": int,
        "fstype": str,
        "host": str,
        "mounted_device": str,
        "mountpoint": str,
        "name": str,
        "path": str,
        "total_blocks": int,
        "total_size": int,
    },
)
TYPE_MEMINFO = TypedDict(
    "TYPE_MEMINFO",
    {
        "host": str,
        "totalram": float,
    },
)
