from __future__ import annotations

from dataclasses import dataclass

from app.users import User

from app.users import LocalUser, ForeignUser


LOCAL_PHONE_PREFIX = "+7"

INVALID_FORMAT: str = "Invalid format of raw_call"
INVALID_CALL_ID: str = "Invalid call id"


class BaseCallException(ValueError):
    def __init__(self, raw_call: str, message: str = "") -> None:
        self.raw_call = raw_call
        self.message = message
        super().__init__(f"{self.message} - {raw_call}")

    def what(self):
        pass


class CallFormatException(BaseCallException):

    def what(self):
        print(f"{self.message}- {self.raw_call}")


class InvalidPhoneCall(BaseCallException):

    def what(self):
        print(f"{self.message} - {self.raw_call}")


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
        self.cross_boarders_idx: set[int] = set()
        self.locals_idx: set[int] = set()

    def get_abonent(self, data) -> User:
        try:
            abonent_data: tuple[int, str, str] = tuple([
                int(item) if i == 0 else item for i, item in enumerate(data)])

        except ValueError:
            raise CallFormatException(",".join(data), INVALID_CALL_ID)

        abonent: User = LocalUser(*abonent_data) if abonent_data[2].startswith(
            LOCAL_PHONE_PREFIX) else ForeignUser(*abonent_data)

        return abonent

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_name,reciever_id,reciever_name,reciever_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        parsed_raw_call: list[str] = list(raw_call.split(","))
        if len(parsed_raw_call) != 6:
            raise CallFormatException(raw_call, INVALID_FORMAT)

        caller: User = self.get_abonent(parsed_raw_call[:3])
        receiver: User = self.get_abonent(parsed_raw_call[3:])

        if caller.id == receiver.id or caller.phone == receiver.phone:
            raise InvalidPhoneCall(raw_call, "Identical caller and receiver")

        call = ActiveCall(caller, receiver)
        self._active_calls.append(call)
        if call.is_cross_border:
            self.cross_boarders_idx.add(len(self._active_calls) - 1)
        else:
            self.locals_idx.add(len(self._active_calls) - 1)
        return call

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return len(self.cross_boarders_idx)
