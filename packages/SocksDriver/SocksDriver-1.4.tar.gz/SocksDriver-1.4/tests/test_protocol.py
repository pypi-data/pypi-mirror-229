from json import loads
from random import choice
from string import ascii_letters, digits, punctuation
from pytest import mark
from SocksDriver import SocksClient

ALPHANUMERIC = ascii_letters + digits


def generate_random_string(num_strings: int, len_strings: int) -> list[str]:
    result = []

    for _ in range(num_strings):
        result.append("".join(choice(ALPHANUMERIC) for _ in range(len_strings)))

    return result


def generate_random_punctuation(num_strings: int, len_strings: int) -> list[str]:
    result = []

    for _ in range(num_strings):
        result.append("".join(choice(punctuation) for _ in range(len_strings)))

    return result


# OS specific line break tests


def test_handle_line_feed(client: SocksClient) -> None:
    result = loads(client.send("foobar\nabc"))
    assert result["status"] == "foobar\nabc"


def test_handle_line_feed_strip_newline(client: SocksClient) -> None:
    result = loads(client.send("foobar\n"))
    assert result["status"] == "foobar"


def test_handle_carriage_return(client: SocksClient) -> None:
    result = loads(client.send("foobar\rabc"))
    assert result["status"] == "foobar\rabc"


def test_handle_carriage_return_strip_carriage_return(client: SocksClient) -> None:
    result = loads(client.send("foobar\r"))
    assert result["status"] == "foobar"


@mark.xfail(
    reason="The nlohmann/json library strips the newline but not the carriage return"
)
def test_handle_end_of_line_strip_end_of_line(client: SocksClient) -> None:
    result = loads(client.send("foobar\r\n"))
    assert result["status"] == "foobar"


def test_handle_end_of_line(client: SocksClient) -> None:
    result = loads(client.send("foobar\r\nabc"))
    assert result["status"] == "foobar\r\nabc"


# Test "empty" messages
# Note that a true empty message, '', would be considered an EOF / hangup by the server


def test_handle_single_line_feed(client: SocksClient) -> None:
    result = loads(client.send("\n"))
    assert result["status"] == ""


def test_handle_single_carriage_return(client: SocksClient) -> None:
    result = loads(client.send("\r"))
    assert result["status"] == ""


@mark.xfail(
    reason="The nlohmann/json library strips the newline but not the carriage return"
)
def test_handle_single_end_of_line(client: SocksClient) -> None:
    result = loads(client.send("\r\n"))
    assert result["status"] == ""


# Echo tests


@mark.parametrize("string", generate_random_string(num_strings=10, len_strings=15))
def test_echo_15_byte_string(client: SocksClient, string: str) -> None:
    result = loads(client.send(string))
    assert string == result["status"]


@mark.parametrize("string", generate_random_punctuation(num_strings=10, len_strings=15))
def test_echo_15_byte_punctuation(client: SocksClient, string: str) -> None:
    result = loads(client.send(string))
    assert string == result["status"]


@mark.skip(reason="Driver does not know how to handle buffer overflow")
def test_echo_max_size_minus_one_byte_string(client: SocksClient) -> None:
    string = generate_random_string(num_strings=1, len_strings=client.BUFFER_SIZE)
    assert string[0] == client.send(string[0])


@mark.skip(reason="Driver does not know how to handle buffer overflow")
def test_echo_max_size_plus_five_bytes_string(client: SocksClient) -> None:
    string = generate_random_string(num_strings=1, len_strings=client.BUFFER_SIZE + 5)
    first_chunk = string[0][0:1024]

    # What happens to string[0][1024:] data??
    # Gets left over in buffer and will screw up the next call
    # Any unit test placed in this file after this test will fail
    assert first_chunk == client.send(string[0])
