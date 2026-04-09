from __future__ import annotations

from dataclasses import dataclass

from app.users import User, LocalUser, ForeignUser

LOCAL_PHONE_PREFIX = "+7"


@dataclass(slots=True)
class ActiveCall:
    caller: User
    receiver: User

    @property
    def is_cross_border(self) -> bool:
        return type(self.caller) is not type(self.receiver)


class Switchboard:
    def __init__(self) -> None:
        self._registry: list[ActiveCall] = []
        self._cross_border_total: int = 0

    def register_call(self, raw_call: str) -> ActiveCall:
        components = self._extract_components(raw_call)

        caller = self._make_user(*components[:3])
        receiver = self._make_user(*components[3:])

        if caller.id == receiver.id:
            raise ValueError("Caller and receiver must be different users")

        call_record = ActiveCall(caller=caller, receiver=receiver)
        self._registry.append(call_record)

        if call_record.is_cross_border:
            self._cross_border_total += 1

        return call_record

    def _extract_components(self, raw: str) -> list[str]:
        """Извлекает и валидирует 6 полей из сырой строки"""
        parts = [p.strip() for p in raw.split(",")]

        if len(parts) != 6:
            raise ValueError("raw_call must contain exactly 6 arguments")

        id_fields = [parts[0], parts[3]]
        name_fields = [parts[1], parts[4]]
        phone_fields = [parts[2], parts[5]]

        if not all(id_fields):
            raise ValueError("User id cannot be empty")
        if not all(name_fields):
            raise ValueError("User fullname cannot be empty")
        if not all(phone_fields):
            raise ValueError("How do you call without a phone?")

        return parts

    def _make_user(self, uid: str, name: str, phone: str) -> User:
        """Метод создания пользователя с полной валидацией"""
        try:
            parsed_id = int(uid)
        except ValueError as err:
            raise ValueError("User id must be an integer") from err

        if parsed_id < 1:
            raise ValueError("User id must be positive")

        if not name.strip():
            raise ValueError("User fullname cannot be empty")

        for char in name:
            if not (char.isalpha() or char.isspace()):
                raise ValueError("User fullname must contain only letters and spaces")

        if not any(c.isalpha() for c in name):
            raise ValueError("User fullname must contain at least one letter")

        self._ensure_valid_phone(phone)

        user_cls = LocalUser if phone.startswith(LOCAL_PHONE_PREFIX) else ForeignUser
        return user_cls(id=parsed_id, fullname=name, phone=phone)

    def _ensure_valid_phone(self, phone: str) -> None:
        """Валидация формата телефонного номера"""
        if not phone or phone[0] != "+":
            raise ValueError("User phone must start with '+'")

        digits = phone[1:]
        if not digits or not digits.isdigit():
            raise ValueError("User phone must contain only digits after '+'")

        if not (7 <= len(digits) <= 15):
            raise ValueError("User phone must be between 7 and 15 digits")

    def get_active_calls_count(self) -> int:
        """Возвращает количество активных звонков. Сложность: O(1)"""
        return len(self._registry)

    def get_cross_border_calls_count(self) -> int:
        """Возвращает количество международных звонков. Сложность: O(1)"""
        return self._cross_border_total
