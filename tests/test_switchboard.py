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


# === НОВЫЕ ТЕСТЫ ДЛЯ ВАЛИДАЦИИ ===

def test_fields_are_trimmed_automatically() -> None:
    """Проверка, что пробелы вокруг значений удаляются."""
    sb = Switchboard()
    result = sb.register_call(
        " 5 , Anna Karenina , +79991112222 , 6 , Leo Tolstoy , +15553334444 "
    )
    assert result.caller.id == 5
    assert result.caller.fullname == "Anna Karenina"
    assert result.receiver.phone == "+15553334444"


def test_local_to_local_not_cross_border() -> None:
    sb = Switchboard()
    call = sb.register_call("1,A,+79990000001,2,B,+79990000002")
    assert call.is_cross_border is False
    assert sb.get_cross_border_calls_count() == 0


def test_foreign_to_foreign_not_cross_border() -> None:
    sb = Switchboard()
    call = sb.register_call("1,A,+15551234567,2,B,+33123456789")
    assert call.is_cross_border is False


def test_foreign_to_local_is_cross_border() -> None:
    """Звонок из-за рубежа в РФ тоже считается международным."""
    sb = Switchboard()
    call = sb.register_call("7,Hans,+4915112345678,8,Dmitry,+79998887766")
    assert call.is_cross_border is True
    assert sb.get_cross_border_calls_count() == 1


# === ТЕСТЫ НА ОБРАБОТКУ НЕВАЛИДНЫХ ДАННЫХ ===

def test_invalid_field_count_raises_error() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="raw_call must contain exactly 6 arguments"):
        sb.register_call("1,A,+7999,2,B")
    with pytest.raises(ValueError, match="raw_call must contain exactly 6 arguments"):
        sb.register_call("1,A,+7999,2,B,+1555,extra_field")


def test_empty_id_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User id cannot be empty"):
        sb.register_call("  ,Alice,+79990000000,2,Bob,+15551234567")


def test_non_integer_id_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User id must be an integer"):
        sb.register_call("abc,Alice,+79990000000,2,Bob,+15551234567")
    with pytest.raises(ValueError, match="User id must be an integer"):
        sb.register_call("12 34,Alice,+79990000000,2,Bob,+15551234567")


def test_negative_id_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User id must be positive"):
        sb.register_call("-10,Alice,+79990000000,2,Bob,+15551234567")


def test_empty_name_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User fullname cannot be empty"):
        sb.register_call("1,   ,+79990000000,2,Bob,+15551234567")


def test_name_with_digits_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User fullname must contain only letters and spaces"):
        sb.register_call("1,Alice123,+79990000000,2,Bob,+15551234567")


def test_name_with_symbols_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User fullname must contain only letters and spaces"):
        sb.register_call("1,Alice@Home,+79990000000,2,Bob,+15551234567")


def test_name_only_numbers_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError):
        sb.register_call("1,12345,+79990000000,2,Bob,+15551234567")


def test_empty_phone_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="How do you call without a phone?"):
        sb.register_call("1,Alice,   ,2,Bob,+15551234567")


def test_phone_no_plus_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match=r"User phone must start with '\+'"):
        sb.register_call("1,Alice,79990000000,2,Bob,+15551234567")


def test_phone_with_letters_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match=r"User phone must contain only digits after '\+'"):
        sb.register_call("1,Alice,+7abc123,2,Bob,+15551234567")


def test_phone_with_spaces_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match=r"User phone must contain only digits after '\+'"):
        sb.register_call("1,Alice,+7 999 000,2,Bob,+15551234567")


def test_phone_too_short_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User phone must be between 7 and 15 digits"):
        sb.register_call("1,Alice,+12345,2,Bob,+15551234567")


def test_phone_too_long_raises() -> None:
    sb = Switchboard()
    with pytest.raises(ValueError, match="User phone must be between 7 and 15 digits"):
        sb.register_call("1,Alice,+12345678901234567,2,Bob,+15551234567")


def test_phone_boundary_lengths_accepted() -> None:
    sb = Switchboard()
    # 7 цифр после +
    c1 = sb.register_call("1,A,+1234567,2,B,+15551234567")
    assert c1.caller.phone == "+1234567"
    # 15 цифр после +
    c2 = sb.register_call("3,C,+123456789012345,4,D,+15551234567")
    assert c2.caller.phone == "+123456789012345"


def test_same_user_cannot_call_themselves() -> None:
    """Проверка: абонент не может быть и звонящим, и принимающим."""
    sb = Switchboard()
    with pytest.raises(ValueError, match="Caller and receiver must be different users"):
        sb.register_call("99,Self,+79990000000,99,Self,+79990000000")


def test_failed_call_does_not_increment_counters() -> None:
    """Невалидный звонок не должен влиять на статистику."""
    sb = Switchboard()
    sb.register_call("1,A,+79990000000,2,B,+15551234567")

    with pytest.raises(ValueError):
        sb.register_call("bad,A,+79990000000,2,B,+15551234567")

    assert sb.get_active_calls_count() == 1
    assert sb.get_cross_border_calls_count() == 1
