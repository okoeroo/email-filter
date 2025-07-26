from icalendar import Calendar
from support.filter_support import apply_filter_on_fulltext_by_keywords


def read_ics_to_text(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        full_text = read_ics_from_bytes_to_text(f.read())
    return full_text


def read_ics_from_bytes_to_text(data: bytes) -> str:
    ### TODO: Should add try except or None check
    try:
        gcal = Calendar.from_ical(data)
    except:
        return None

    elements = []

    for component in gcal.walk():
        if component.name != "VEVENT":
            continue

        for key, value in component.items():
            if key != "SUMMARY" and key != "DESCRIPTION" and key != "LOCATION" and key != "ATTENDEE" and key != "LOCATION":
                continue

            # Still in bytes?
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except Exception:
                    continue

            # Append
            if value:
                elements.append(key)
                elements.append(str(value))

    return "\n".join(elements)


# IMPORTANT: time is more complicated to judge. Hence, no timeframe matching is done here.
def apply_ics_filters(config: dict, context: dict) -> dict:
    context['ret_ics_keyword_matched'] = False
    full_text: str = context['gcal_full_text']

    results = apply_filter_on_fulltext_by_keywords(config['filter']['keywords']['list_of_keywords'], full_text)
    context['keyword_match'] = results
    context['ret_ics_keyword_matched'] = bool(results)

    return context


def verdict_ics_filter_output(context: dict) -> bool:
    return bool(context.get('keyword_match'))

