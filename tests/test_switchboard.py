import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


def test_register_call_creates_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_counts_active_calls() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "3,John Smith,+15551234567,4,Jane Doe,+33123456789"
    )

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Petr Petrov,+78880000000,4,Maria Petrova,+79991112233"
    )
    switchboard.register_call(
        "5,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1

# ====== НОВЫЕ ТЕСТЫ ========

def test_register_call_foreign_to_local() -> None:
    """Проверка, что обратный звонок (Foreign -> Local) также считается международным."""
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "10,John Doe,+15551234567,11,Иван Иванов,+79991234567"
    )

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert active_call.is_cross_border is True
    assert switchboard.get_active_calls_count() == 1
    assert switchboard.get_cross_border_calls_count() == 1


def test_register_call_raises_error_on_missing_args() -> None:
    """Проверка выброса исключения, если передано меньше 6 параметров в raw_call."""
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Неверный формат строки raw_call"):
        switchboard.register_call("1,Иван,+79990000000,2,Петр")


def test_register_call_raises_error_on_non_numeric_id() -> None:
    """Проверка, что передача строки вместо числа в id вызывает ValueError."""
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call("один,Иван,+79990000000,2,John,+15551234567")


def test_register_call_raises_error_on_empty_name() -> None:
    """Проверка срабатывания валидации базового класса User.__post_init__ при пустом имени."""
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="User fullname cannot be empty"):
        switchboard.register_call("1,   ,+79990000000,2,John,+15551234567")
