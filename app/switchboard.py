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
        self._active_calls: list[ActiveCall] = []
        self._cross_border_calls_count: int = 0

    def register_call(self, raw_call: str) -> ActiveCall:
        parts = raw_call.split(",")
        if len(parts) != 6:
            raise ValueError("Неверный формат строки raw_call")

        caller_id_str, caller_name, caller_phone, receiver_id_str, receiver_name, receiver_phone = parts

        caller_id = int(caller_id_str)
        receiver_id = int(receiver_id_str)

        if caller_phone.startswith(LOCAL_PHONE_PREFIX):
            caller = LocalUser(id=caller_id, fullname=caller_name, phone=caller_phone)
        else:
            caller = ForeignUser(id=caller_id, fullname=caller_name, phone=caller_phone)

        if receiver_phone.startswith(LOCAL_PHONE_PREFIX):
            receiver = LocalUser(id=receiver_id, fullname=receiver_name, phone=receiver_phone)
        else:
            receiver = ForeignUser(id=receiver_id, fullname=receiver_name, phone=receiver_phone)

        active_call = ActiveCall(caller=caller, receiver=receiver)
        self._active_calls.append(active_call)

        if active_call.is_cross_border:
            self._cross_border_calls_count += 1

        return active_call

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls_count
