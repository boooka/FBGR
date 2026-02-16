"""
Утилиты: форматирование чисел для JSON, сериализация строк БД.
"""
from decimal import Decimal, ROUND_HALF_UP


def round_rnd(value, decimals=0):
    """Форматирование числа до заданного количества знаков после запятой."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return round(float(value), decimals)
    d = Decimal(str(value))
    return float(d.quantize(Decimal(10) ** -decimals, rounding=ROUND_HALF_UP))


def round_rnd4(value):
    """Форматирование числа до 4 знаков после запятой."""
    return round_rnd(value, 4)


def serialize_row(row):
    """Преобразует строку из БД в JSON-сериализуемый dict (даты, Decimal)."""
    out = {}
    for k, v in row.items():
        if v is None:
            out[k] = None
        elif hasattr(v, 'isoformat'):
            out[k] = v.isoformat()
        elif hasattr(v, 'numerator'):
            out[k] = round_rnd4(float(v)) if isinstance(v, Decimal) else (int(v) if v == int(v) else float(v))
        else:
            out[k] = v
    return out
