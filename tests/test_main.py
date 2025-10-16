from main import create_echo_reply


def test_create_echo_reply_returns_same_text() -> None:
    text = "hello world"
    assert create_echo_reply(text) == text


def test_create_echo_reply_handles_empty_input() -> None:
    assert create_echo_reply("") == ""
    assert create_echo_reply(None) == ""
