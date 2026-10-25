import datetime
import unittest

from coptic_calendar import (
    CopticDate,
    coptic_to_gregorian,
    gregorian_to_coptic,
    is_coptic_leap_year,
    COPTIC_EPOCH,
    MONTH_NAMES,
)


class TestEpoch(unittest.TestCase):
    def test_epoch_is_284_08_29(self):
        self.assertEqual(
            COPTIC_EPOCH,
            datetime.date(284, 8, 29).toordinal(),
        )


class TestMonthNames(unittest.TestCase):
    def test_has_13_months(self):
        self.assertEqual(len(MONTH_NAMES), 13)

    def test_nasi_is_thirteenth(self):
        self.assertEqual(MONTH_NAMES[12], "Nasi")


class TestLeapYear(unittest.TestCase):
    def test_year_3_is_leap(self):
        self.assertTrue(is_coptic_leap_year(3))

    def test_year_7_is_leap(self):
        self.assertTrue(is_coptic_leap_year(7))

    def test_year_1_is_not_leap(self):
        self.assertFalse(is_coptic_leap_year(1))

    def test_year_4_is_not_leap(self):
        self.assertFalse(is_coptic_leap_year(4))


class TestEpochConversion(unittest.TestCase):
    def test_tout_1_1_is_epoch(self):
        self.assertEqual(coptic_to_gregorian(1, 1, 1), datetime.date(284, 8, 29))

    def test_round_trip_epoch(self):
        self.assertEqual(
            gregorian_to_coptic(datetime.date(284, 8, 29)), (1, 1, 1)
        )


class TestReferenceDate(unittest.TestCase):
    def test_11_sep_2024_is_tout_1741_1(self):
        # 2024-09-11 is Tout 1, 1741 in the Coptic calendar.
        self.assertEqual(
            gregorian_to_coptic(datetime.date(2024, 9, 11)), (1741, 1, 1)
        )

    def test_tout_1741_1_is_11_sep_2024(self):
        self.assertEqual(
            coptic_to_gregorian(1741, 1, 1), datetime.date(2024, 9, 11)
        )


class TestLeapDay(unittest.TestCase):
    def test_nasi_has_6_days_in_leap_year_3(self):
        # Coptic year 3 (mod 4 == 3) is a leap year; Nasi (month 13) has 6 days.
        # Year 3 starts 286-08-29 (epoch + 2*365 = 286-08-29, no prior leap years).
        # Nasi 6, year 3 = 286-08-29 + 365 = 287-08-29 (last day of leap year 3).
        g = coptic_to_gregorian(3, 13, 6)
        self.assertEqual(g, datetime.date(287, 8, 29))

    def test_nasi_day_6_in_non_leap_year_raises(self):
        with self.assertRaises(ValueError):
            coptic_to_gregorian(1, 13, 6)

    def test_gregorian_to_coptic_finds_nasi_in_leap_year(self):
        # Verify that the extra day is reachable by round-trip
        cd = (3, 13, 6)
        g = coptic_to_gregorian(*cd)
        self.assertEqual(gregorian_to_coptic(g), cd)


class TestCopticDateClass(unittest.TestCase):
    def test_properties(self):
        cd = CopticDate(1741, 1, 1)
        self.assertEqual(cd.year, 1741)
        self.assertEqual(cd.month, 1)
        self.assertEqual(cd.day, 1)
        self.assertEqual(cd.month_name, "Tout")

    def test_to_gregorian(self):
        cd = CopticDate(1741, 1, 1)
        self.assertEqual(cd.to_gregorian(), datetime.date(2024, 9, 11))

    def test_from_gregorian_round_trip(self):
        # Year 3 (mod 4 == 3) is a leap year with Nasi 6.
        cd = CopticDate(3, 13, 6)
        g = cd.to_gregorian()
        cd2 = CopticDate.from_gregorian(g)
        self.assertEqual(cd, cd2)

    def test_repr(self):
        cd = CopticDate(1741, 1, 1)
        self.assertEqual(repr(cd), "CopticDate(1741, 1, 1)")

    def test_equality(self):
        a = CopticDate(1741, 1, 1)
        b = CopticDate(1741, 1, 1)
        c = CopticDate(1741, 1, 2)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_invalid_month_raises(self):
        with self.assertRaises(ValueError):
            CopticDate(1741, 14, 1)

    def test_invalid_day_raises(self):
        with self.assertRaises(ValueError):
            CopticDate(1741, 1, 31)

    def test_hashable(self):
        s = {CopticDate(1741, 1, 1), CopticDate(1741, 1, 1)}
        self.assertEqual(len(s), 1)


class TestRoundTripMany(unittest.TestCase):
    def test_round_trip_sample_dates(self):
        samples = [
            datetime.date(2024, 9, 11),
            datetime.date(2025, 1, 7),
            datetime.date(284, 8, 29),
            datetime.date(1582, 10, 4),
        ]
        for g in samples:
            y, m, d = gregorian_to_coptic(g)
            self.assertEqual(coptic_to_gregorian(y, m, d), g, f"Failed round-trip for {g}")

    def test_nasi_boundary_leap_year(self):
        # Test the day after Nasi 6 in a leap year: should be Tout 1 of the next year
        nasi_6_leap = coptic_to_gregorian(3, 13, 6)
        tout_1_next = coptic_to_gregorian(4, 1, 1)
        self.assertEqual((nasi_6_leap + datetime.timedelta(days=1)), tout_1_next)

    def test_nasi_boundary_common_year(self):
        # Test the day after Nasi 5 in a common year: should be Tout 1 of the next year
        nasi_5_common = coptic_to_gregorian(1, 13, 5)
        tout_1_next = coptic_to_gregorian(2, 1, 1)
        self.assertEqual((nasi_5_common + datetime.timedelta(days=1)), tout_1_next)


if __name__ == "__main__":
    unittest.main()
