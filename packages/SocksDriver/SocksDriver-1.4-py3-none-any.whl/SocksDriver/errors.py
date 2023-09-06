class SocksConnectionError(Exception):
    """Handle all connection errors."""


class SocksTransmissionError(Exception):
    """Handle all data transmission errors."""


class SocksInternalServerError(Exception):
    """Handle server-side errors."""
