from client import HumanPlayer


def mock_input(inputs):
    return "0"


def mock_print(*args):
    pass


def mock_input_pass(inputs):
    return "-1"


def test_call_turn_strategy(monkeypatch):
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.setattr("builtins.print", mock_print)

    h = HumanPlayer(0)
    assert h.call_strategy([0, 1, 2], "1") == 0


def test_call_turn_strategy_pass(monkeypatch):
    monkeypatch.setattr("builtins.input", mock_input_pass)
    monkeypatch.setattr("builtins.print", mock_print)

    h = HumanPlayer(0)
    assert not h.call_strategy([0, 1, 2], "1")
