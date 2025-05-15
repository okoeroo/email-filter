from icalendar import Calendar
from datetime import datetime
from support.filter_support import find_exact_word


"""
with open('calendar.ics', 'rb') as f:
    gcal = Calendar.from_ical(f.read())

for component in gcal.walk():
    if component.name == "VEVENT":
        print(component.get("summary"), component.get("dtstart").dt, component.get("dtend").dt)
"""


def read_ics(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        gcal = Calendar.from_ical(f.read())

    return gcal


# IMPORTANT: time is more complicated to judge. Hence, no timeframe matching is done here.
def apply_ics_filters(config: dict, context: dict) -> dict:
    gcal: Calendar = context['gcal']

    context['ret_ics_keyword_matched'] = False

    # input keywords to match
    keywords = config['keywords']

    for component in gcal.walk():
        if component.name != "VEVENT":
            continue

        for key, value in component.items():
            if config['verbose']:
                print(f"key {key} value {value}")

            if key != "SUMMARY" and key != "DESCRIPTION" and key != "LOCATION" and key != "ATTENDEE":
                continue

            # Still in bytes?
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except Exception:
                    continue

            # Value conversion from object to str representation of the value
            value_decoded = str(value) if value else ""

            ### Matching
            for item in keywords:
                results = find_exact_word(value_decoded, item)
                context['ret_ics_keyword_matched'] = bool(results)
                context['keyword_match'] = results
                if bool(results):
                    return context

    return context


def verdict_ics_filter_output(context: dict) -> bool:
    return bool(context.get('keyword_match'))