from datetime import date, timedelta
import re
import calendar

WORD_NUMBERS: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

MONTH_MAP: dict[str, int] = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

WEEKDAY_MAP: dict[str, int] = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thur": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}

_MONTHS = "|".join(sorted(MONTH_MAP, key=len, reverse=True))
_WEEKDAYS = "|".join(sorted(WEEKDAY_MAP, key=len, reverse=True))
_UNITS = r"years?|months?|weeks?|days?"

_ONES_STR = r"nine|eight|seven|six|five|four|three|two|one"
_SMALL_STR = r"nineteen|eighteen|seventeen|sixteen|fifteen|fourteen|thirteen|twelve|eleven|ten|nine|eight|seven|six|five|four|three|two|one|zero"
_TENS_STR = r"ninety|eighty|seventy|sixty|fifty|forty|thirty|twenty"
_WORD_NUM = rf"(?:{_TENS_STR})(?:-(?:{_ONES_STR}))?|(?:{_SMALL_STR})"
_NUM = rf"(?:\d+|{_WORD_NUM})"


def _to_int(s: str) -> int:
    if re.fullmatch(r"\d+", s):
        return int(s)
    parts = s.split("-")
    return sum(WORD_NUMBERS[p] for p in parts)


def _add_months(d: date, n: int) -> date:
    month = d.month + n
    year = d.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _next_weekday(ref: date, target: int) -> date:
    days = (target - ref.weekday()) % 7 or 7
    if 1 < days < 7:  # not tomorrow and not same weekday → skip to following week
        days += 7
    return ref + timedelta(days=days)


def _prev_weekday(ref: date, target: int) -> date:
    days = (ref.weekday() - target) % 7 or 7
    return ref - timedelta(days=days)


def _apply_offset(base: date, n: int, unit: str, sign: int) -> date:
    u = unit.rstrip("s")
    if u == "day":
        return base + timedelta(days=sign * n)
    if u == "week":
        return base + timedelta(weeks=sign * n)
    if u == "year":
        return _add_months(base, sign * n * 12)
    return _add_months(base, sign * n)


def _parse_base(s: str, today: date) -> date:
    """Parse a simple date string: absolute date or today/tomorrow/yesterday."""
    if s in ("today", "now"):
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)
    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if iso:
        return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
    m = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(
        rf"({_MONTHS})\.?\s+(\d+)(?:st|nd|rd|th)?(?:[,\s]+(\d{{4}}))?",
        s,
        re.IGNORECASE,
    )
    if m:
        month = MONTH_MAP[m.group(1).lower()]
        day = int(m.group(2))
        year = int(m.group(3)) if m.group(3) else today.year
        return date(year, month, day)
    m = re.fullmatch(
        rf"(?:the\s+)?(\d+)(?:st|nd|rd|th)\s+of\s+({_MONTHS})(?:\s+(\d{{4}}))?",
        s,
        re.IGNORECASE,
    )
    if m:
        day = int(m.group(1))
        month = MONTH_MAP[m.group(2).lower()]
        year = int(m.group(3)) if m.group(3) else today.year
        return date(year, month, day)
    raise ValueError(f"Cannot parse date expression: {s!r}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    t = s.strip().lower()

    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", t)
    if iso:
        return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))

    if t == "today":
        return today
    if t == "tomorrow":
        return today + timedelta(days=1)
    if t == "yesterday":
        return today - timedelta(days=1)
    if t == "the day after tomorrow":
        return today + timedelta(days=2)
    if t == "next week":
        return today + timedelta(weeks=1)

    m = re.fullmatch(rf"in ({_NUM}) ({_UNITS})", t)
    if m:
        return _apply_offset(today, _to_int(m.group(1)), m.group(2), 1)

    m = re.fullmatch(rf"({_NUM}) ({_UNITS}) from (.+)", t)
    if m:
        base = _parse_base(m.group(3), today)
        return _apply_offset(base, _to_int(m.group(1)), m.group(2), 1)

    m = re.fullmatch(rf"({_NUM}) ({_UNITS}) ago", t)
    if m:
        return _apply_offset(today, _to_int(m.group(1)), m.group(2), -1)

    m = re.fullmatch(rf"next ({_WEEKDAYS})", t)
    if m:
        return _next_weekday(today, WEEKDAY_MAP[m.group(1)])

    m = re.fullmatch(rf"last ({_WEEKDAYS})", t)
    if m:
        return _prev_weekday(today, WEEKDAY_MAP[m.group(1)])

    m = re.fullmatch(rf"({_NUM}) years? and ({_NUM}) months? (before|after) (.+)", t)
    if m:
        base = _parse_base(m.group(4), today)
        total = _to_int(m.group(1)) * 12 + _to_int(m.group(2))
        sign = 1 if m.group(3) == "after" else -1
        return _add_months(base, sign * total)

    m = re.fullmatch(rf"({_NUM}) ({_UNITS}) (before|after) (.+)", t)
    if m:
        base = _parse_base(m.group(4), today)
        sign = 1 if m.group(3) == "after" else -1
        return _apply_offset(base, _to_int(m.group(1)), m.group(2), sign)

    return _parse_base(t, today)
