from __future__ import annotations
from enum import IntEnum


class Result:
    class Status(IntEnum):
        SUCCESS = 0
        FAILED_WITH_COMPLETION = 1

        def __bool__(self) -> bool:
            return self == Result.Status.SUCCESS

    status: Status
    message: str

    def __init__(self, status: Status, message: str = "") -> None:
        self.status = status
        self.message = message

    @classmethod
    def success(cls, message: str = "") -> Result:
        return Result(Result.Status.SUCCESS, message)

    @classmethod
    def failed(cls, message: str = "") -> Result:
        return Result(Result.Status.FAILED_WITH_COMPLETION, message)

    def __bool__(self) -> bool:
        return self.status == Result.Status.SUCCESS
