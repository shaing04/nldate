from datetime import date
from nldate import parse


def test_1():
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_2():
    assert parse("Jan 11th 2011") == date(2011, 1, 11)


fake_today = date(2025, 5, 11)


def test_3():

    assert parse("tomorrow", today=fake_today) == date(2025, 5, 12)


def test_4():
    assert parse("next week", today=fake_today) == date(2025, 5, 18)


def test_5():
    assert parse("in 3 days", today=fake_today) == date(2025, 5, 14)


def test_6():
    assert parse("yesterday", today=fake_today) == date(2025, 5, 10)


def test_7():
    assert parse("2 weeks ago", today=fake_today) == date(2025, 4, 27)


def test_8():
    assert parse("next Friday", today=fake_today) == date(2025, 5, 23)


def test_9():
    assert parse("last Wednesday", today=fake_today) == date(2025, 5, 7)


def test_10():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)


def test_11():
    assert parse("2 months after March 8th", today=date(2025, 1, 1)) == date(2025, 5, 8)


def test_12():
    assert parse("today", today=fake_today) == date(2025, 5, 11)


def test_13():
    assert parse("the day after tomorrow", today=fake_today) == date(2025, 5, 13)


def test_14():
    assert parse("3 months from now", today=fake_today) == date(2025, 8, 11)


def test_15():
    assert parse("1 year and 2 months after yesterday", today=fake_today) == date(
        2026, 7, 10
    )


def test_16():
    assert parse("next Monday", today=fake_today) == date(2025, 5, 12)


def test_17():
    assert parse("2025-12-04") == date(2025, 12, 4)


def test_18():
    assert parse("3 days from 2025-12-04") == date(2025, 12, 7)
