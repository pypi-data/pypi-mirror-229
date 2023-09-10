from typing import TypeVar

T = TypeVar('T')


class GlobalVariable:
    __variable: dict = {}

    @staticmethod
    def set(name: str, value: T):
        GlobalVariable.__variable[name] = value

    @staticmethod
    def get(name: str, default_value: any = None) -> T:
        if name not in GlobalVariable.__variable:
            return default_value
        return GlobalVariable.__variable[name]

    @staticmethod
    def get_or_fail(name: str) -> T:
        if name not in GlobalVariable.__variable:
            raise Exception("This variable has not been initialized")
        return GlobalVariable.__variable[name]
