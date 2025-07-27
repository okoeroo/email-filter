import aiofiles
from icalendar import Calendar
from support.filter_support import apply_filter_on_fulltext_by_keywords


async def read_ics_to_text(filepath: str) -> str | None:
    async with aiofiles.open(filepath, 'rb') as f:
        data = await f.read()
    
    return read_ics_from_bytes_to_text(data)


def read_ics_from_bytes_to_text(data: bytes) -> str | None:
    try:
        gcal = Calendar.from_ical(data)
    except Exception as e:
        # Log eventueel de fout
        return None

    elements = []
    interesting_keys = {"SUMMARY", "DESCRIPTION", "LOCATION", "ATTENDEE"}

    for component in gcal.walk():
        if component.name != "VEVENT":
            continue

        for key, value in component.items():
            if key not in interesting_keys:
                continue

            # Decode bytes
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except Exception:
                    continue

            # Sommige velden kunnen meerdere waarden hebben
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)

            if value:
                elements.append(key)
                elements.append(str(value))

    return "\n".join(elements) if elements else None


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

