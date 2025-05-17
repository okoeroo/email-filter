from docx import Document
from io import BytesIO
from support.filter_support import find_exact_word


def read_docx_from_bytes(data: bytes) -> Document:
    return Document(BytesIO(data))


def read_docx(filepath: str) -> Document:
    with open(filepath, "rb") as f:
        raw_bytes = f.read()
    return read_docx_from_bytes(raw_bytes)


# IMPORTANT: time is more complicated to judge. Hence, no timeframe matching is done here.
def apply_docx_filters(config: dict, context: dict) -> dict:
    doc: Document = context['docx']

    context['ret_docx_keyword_matched'] = False

    # input keywords to match
    keywords = config['keywords']

    full_text = ""
    for para in doc.paragraphs:
        full_text += para.text

        ### Matching
        for item in keywords:
            results = find_exact_word(full_text, item)
            context['ret_docx_keyword_matched'] = bool(results)
            context['keyword_match'] = results
            if bool(results):
                return context

    return context


def verdict_docx_filter_output(context: dict) -> bool:
    return bool(context.get('keyword_match'))


def apply_docx_filters_as_attachment(config: dict, doc: Document) -> list[str]:
    # input keywords to match
    keywords = config['keywords']

    full_text = ""
    for para in doc.paragraphs:
        full_text += para.text

        ### Matching
        for item in keywords:
            keyword_match = find_exact_word(full_text, item)
            if bool(keyword_match):
                return keyword_match

    return None
