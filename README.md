# coptic-calendar

A small, zero-dependency Python library for converting dates between the Coptic and (proleptic) Gregorian calendars.

## Usage

```python
import datetime
from coptic_calendar import CopticDate, gregorian_to_coptic, coptic_to_gregorian

# Gregorian → Coptic tuple
y, m, d = gregorian_to_coptic(datetime.date(2024, 9, 11))
# (1741, 1, 13) — Tout 13, year 1741

# Coptic tuple → Gregorian date
g = coptic_to_gregorian(1741, 1, 13)
# datetime.date(2024, 9, 11)

# Or use the immutable CopticDate class
cd = CopticDate(1741, 1, 13)
cd.to_gregorian()        # datetime.date(2024, 9, 11)
cd.month_name            # 'Tout'
CopticDate.from_gregorian(datetime.date(2024, 9, 11))  # CopticDate(1741, 1, 13)
```

## Why

The Coptic calendar (a.k.a. the Alexandrian calendar) is the liturgical calendar of the Coptic Orthodox Church and is used throughout Egypt for agricultural and ecclesiastical purposes. Converting between it and the Gregorian calendar is a well-defined but fiddly task: the Coptic year has 13 months (12 of 30 days plus an intercalary "Nasi" of 5 or 6 days), and leap years occur every fourth year on a specific offset (year mod 4 equals 3).

This library exists to give Python developers a single self-contained module for the two-way conversion, with no external dependencies and no ambiguity about how pre-1582 dates are handled: we use the **proleptic Gregorian calendar** throughout (projecting Gregorian rules backward in time), which is the standard computational convention.

## The awkward edge

The most common pitfall is the intercalary month **Nasi** (month 13): it has **5 days in a common year and 6 in a leap year**. Day 6 of Nasi only exists in leap years, and this library rejects it with `ValueError` otherwise. If your input date falls after August 29 of a Gregorian year, double-check which Coptic year it lands in — the Coptic New Year (Tout 1) shifts relative to September because the Coptic year is ~6 minutes shorter than the Gregorian tropical year.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

