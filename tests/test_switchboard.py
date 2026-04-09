import pytest

from app.switchboard import Switchboard, CallFormatException, InvalidPhoneCall, INVALID_CALL_ID, INVALID_FORMAT, VOID_NAME_OR_PHONE
from app.users import ForeignUser, LocalUser

import re


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


def test_register_call_invalid_row_call_format() -> None:
    switchboard = Switchboard()

    raw_call: str = "1,,+79990000000,2,John Smith,+15551234567"
    with pytest.raises(CallFormatException, match=re.escape(f"{VOID_NAME_OR_PHONE} - {raw_call[:3]}")):
        switchboard.register_call(
            raw_call
        )

    raw_call: str = "1, ,+79990000000,2,John Smith,+15551234567"
    with pytest.raises(CallFormatException, match=re.escape(f"{VOID_NAME_OR_PHONE} - {raw_call[:3]}")):
        switchboard.register_call(
            raw_call
        )

    raw_call: str = "1,John, ,2,John Smith,+15551234567"
    with pytest.raises(CallFormatException, match=re.escape(f"{VOID_NAME_OR_PHONE} - {raw_call[:3]}")):
        switchboard.register_call(
            raw_call
        )


def test_register_call_identical_abonents() -> None:
    switchboard = Switchboard()
    with pytest.raises(InvalidPhoneCall):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,1,Ivan Ivanov,+79990000000"
        )

    with pytest.raises(InvalidPhoneCall):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,2,Ivan Ivanov,+79990000000"
        )

    with pytest.raises(InvalidPhoneCall):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,1,Ivan Ivanov,+78990000000"
        )


def test_register_count_calls_no_calls() -> None:
    switchboard = Switchboard()
    assert switchboard.get_active_calls_count() == 0
    assert switchboard.get_cross_border_calls_count() == 0


def test_register_calls_invalid_id() -> None:
    switchboard = Switchboard()
    with pytest.raises(CallFormatException, match=re.escape(f"{INVALID_CALL_ID} - abcd,Jane Doe,+33123456789")):
        switchboard.register_call(
            "abcd,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
        )


def test_register_calls_void_row_call() -> None:
    switchBoard = Switchboard()
    with pytest.raises(CallFormatException):
        switchBoard.register_call("")
