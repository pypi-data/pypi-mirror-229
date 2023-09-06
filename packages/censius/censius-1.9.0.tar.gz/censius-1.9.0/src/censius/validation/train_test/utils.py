from typing import Union
from pydantic import BaseModel


class RangeValid(BaseModel):
    lt: Union[int, float] = None
    gt: Union[int, float] = None
    lte: Union[int, float] = None
    gte: Union[int, float] = None


def parse_int_or_float(s):
    try:
        value = int(s)
    except ValueError:
        try:
            value = float(s)
        except ValueError:
            raise ValueError(f"Cannot parse '{s}' as either integer or float.")
    return value


def get_str(val1, val2, rule_name):
    return f"{parse_int_or_float(val1)}, {rule_name} rule violated got: {val2}"


class CompareUtil:
    @staticmethod
    def lte(val1, val2):
        if val1 <= parse_int_or_float(val2):
            return True
        return False

    @staticmethod
    def gte(val1, val2):
        if val1 >= parse_int_or_float(val2):
            return True
        return False

    @staticmethod
    def gt(val1, val2):
        if val1 > val2:
            return True
        return False

    @staticmethod
    def lt(val1, val2):
        if val1 < parse_int_or_float(val2):
            return True
        return False
