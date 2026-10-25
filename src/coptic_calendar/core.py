from __future__ import annotations

import datetime

# The proleptic Gregorian ordinal day number of 1 Tout year 1 (August 29, 284 CE).
# Source: Standard astronomical conversion; used by the Coptic Orthodox Church liturgical
# calendar. Computed as the Python date.toordinal() of the Gregorian date 284-08-29.
# Note: Gregorian dates before 1582 are "proleptic Gregorian" — i.e., we project the
# Gregorian rules backwards. This is the universal convention for computational calendars.
COPTIC_EPOCH: int = datetime.date(284, 8, 29).toordinal()

MONTH_NAMES = [
    "Tout",
    "Babah",
    "Hatur",
    "Kiyahk",
    "Tubah",
    "Amshir",
    "Baramhat",
    "Baramoudah",
    "Bashans",
    "Paona",
    "Epep",
    "Mesra",
    "Nasi",
]

_DAYS_IN_MONTH = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]


def is_gregorian_leap_year(year: int) -> bool:
    """Leap year in the (proleptic) Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def is_coptic_leap_year(year: int) -> bool:
    """A Coptic year is a leap year when year % 4 == 3.

    The Coptic calendar follows the Julian leap cycle: every fourth year, with the
    leap day added to the epagomenal month Nasi. Because the cycle starts on a
    particular offset, year % 4 == 3 characterises the leap years.
    """
    return year % 4 == 3


def _days_in_coptic_year(year: int) -> int:
    return 365 + (1 if is_coptic_leap_year(year) else 0)


def _validate_coptic_ymd(year: int, month: int, day: int) -> None:
    if month < 1 or month > 13:
        raise ValueError(f"Coptic month must be 1..13, got {month}")
    if day < 1 or day > _days_in_coptic_month(year, month):
        raise ValueError(
            f"Day {day} out of range for month {month} in Coptic year {year}"
        )


def _days_in_coptic_month(year: int, month: int) -> int:
    if month <= 12:
        return _DAYS_IN_MONTH[month - 1]
    return 6 if is_coptic_leap_year(year) else 5


def coptic_to_gregorian(year: int, month: int, day: int) -> datetime.date:
    """Convert a Coptic date to a proleptic Gregorian date.

    The Coptic day starts at sunset in real life, but for computational
    purposes the convention is to treat the Coptic day as aligned to the
    Gregorian day. This is the standard mapping used by liturgical tables.
    """
    _validate_coptic_ymd(year, month, day)
    ordinal = COPTIC_EPOCH
    for y in range(1, year):
        ordinal += _days_in_coptic_year(y)
    for m in range(1, month):
        ordinal += _days_in_coptic_month(year, m)
    ordinal += day - 1
    return datetime.date.fromordinal(ordinal)


def gregorian_to_coptic(g: datetime.date) -> tuple[int, int, int]:
    """Convert a proleptic Gregorian date to a Coptic (year, month, day) tuple."""
    ordinal = g.toordinal()
    days = ordinal - COPTIC_EPOCH
    if days < 0:
        # Walk backward through Coptic years of decreasing year number
        year = 0
        while days < 0:
            year -= 1
            days += _days_in_coptic_year(year)
    else:
        year = 1
        while True:
            d = _days_in_coptic_year(year)
            if days < d:
                break
            days -= d
            year += 1
    month = 1
    while month <= 12 and days >= 30:
        days -= 30
        month += 1
    day = days + 1
    return year, month, day


class CopticDate:
    """An immutable Coptic calendar date.

    Internally we store (year, month, day) and lazily compute the Gregorian
    equivalent. The class is intentionally minimal; it does not implement
    arithmetic beyond what is needed for round-trip conversion testing.
    """

    __slots__ = ("_year", "_month", "_day", "_greg")

    def __init__(self, year: int, month: int, day: int) -> None:
        _validate_coptic_ymd(year, month, day)
        self._year = year
        self._month = month
        self._day = day
        self._greg: datetime.date | None = None

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day

    @property
    def month_name(self) -> str:
        return MONTH_NAMES[self._month - 1]

    def to_gregorian(self) -> datetime.date:
        if self._greg is None:
            self._greg = coptic_to_gregorian(self._year, self._month, self._day)
        return self._greg

    @classmethod
    def from_gregorian(cls, g: datetime.date) -> "CopticDate":
        y, m, d = gregorian_to_coptic(g)
        obj = cls.__new__(cls)
        obj._year = y
        obj._month = m
        obj._day = d
        obj._greg = g
        return obj

    def __repr__(self) -> str:
        return f"CopticDate({self._year}, {self._month}, {self._day})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CopticDate):
            return NotImplemented
        return (
            self._year == other._year
            and self._month == other._month
            and self._day == other._day
        )

    def __hash__(self) -> int:
        return hash((self._year, self._month, self._day))
