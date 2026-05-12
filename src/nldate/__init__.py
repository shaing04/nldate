from datetime import date, timedelta
import re
import calendar

MONTH_MAP: dict[str, int] = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12,
}

WEEKDAY_MAP: dict[str, int] = {
    'monday': 0, 'mon': 0,
    'tuesday': 1, 'tue': 1,
    'wednesday': 2, 'wed': 2,
    'thursday': 3, 'thu': 3, 'thur': 3,
    'friday': 4, 'fri': 4,
    'saturday': 5, 'sat': 5,
    'sunday': 6, 'sun': 6,
}

_MONTHS = '|'.join(sorted(MONTH_MAP, key=len, reverse=True))
_WEEKDAYS = '|'.join(sorted(WEEKDAY_MAP, key=len, reverse=True))
_UNITS = r'months?|weeks?|days?'


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
    u = unit.rstrip('s')
    if u == 'day':
        return base + timedelta(days=sign * n)
    if u == 'week':
        return base + timedelta(weeks=sign * n)
    return _add_months(base, sign * n)


def _parse_base(s: str, today: date) -> date:
    """Parse a simple date string: absolute date or today/tomorrow/yesterday."""
    if s == 'today':
        return today
    if s == 'tomorrow':
        return today + timedelta(days=1)
    if s == 'yesterday':
        return today - timedelta(days=1)
    m = re.fullmatch(
        rf'({_MONTHS})\s+(\d+)(?:st|nd|rd|th)?(?:[,\s]+(\d{{4}}))?',
        s, re.IGNORECASE,
    )
    if m:
        month = MONTH_MAP[m.group(1).lower()]
        day = int(m.group(2))
        year = int(m.group(3)) if m.group(3) else today.year
        return date(year, month, day)
    raise ValueError(f"Cannot parse date expression: {s!r}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    t = s.strip().lower()

    if t == 'today':
        return today
    if t == 'tomorrow':
        return today + timedelta(days=1)
    if t == 'yesterday':
        return today - timedelta(days=1)
    if t == 'the day after tomorrow':
        return today + timedelta(days=2)
    if t == 'next week':
        return today + timedelta(weeks=1)

    m = re.fullmatch(rf'in (\d+) ({_UNITS})', t)
    if m:
        return _apply_offset(today, int(m.group(1)), m.group(2), 1)

    m = re.fullmatch(rf'(\d+) ({_UNITS}) from now', t)
    if m:
        return _apply_offset(today, int(m.group(1)), m.group(2), 1)

    m = re.fullmatch(rf'(\d+) ({_UNITS}) ago', t)
    if m:
        return _apply_offset(today, int(m.group(1)), m.group(2), -1)

    m = re.fullmatch(rf'next ({_WEEKDAYS})', t)
    if m:
        return _next_weekday(today, WEEKDAY_MAP[m.group(1)])

    m = re.fullmatch(rf'last ({_WEEKDAYS})', t)
    if m:
        return _prev_weekday(today, WEEKDAY_MAP[m.group(1)])

    m = re.fullmatch(r'(\d+) years? and (\d+) months? (before|after) (.+)', t)
    if m:
        base = _parse_base(m.group(4), today)
        total = int(m.group(1)) * 12 + int(m.group(2))
        sign = 1 if m.group(3) == 'after' else -1
        return _add_months(base, sign * total)

    m = re.fullmatch(rf'(\d+) ({_UNITS}) (before|after) (.+)', t)
    if m:
        base = _parse_base(m.group(4), today)
        sign = 1 if m.group(3) == 'after' else -1
        return _apply_offset(base, int(m.group(1)), m.group(2), sign)

    return _parse_base(t, today)
