from PyPDF2 import PdfReader
from PyPDF2.generic import NullObject
from io import BytesIO
from support.filter_support import find_exact_word


def read_pdf_from_file(filepath: str) -> PdfReader:
    try:
        reader = PdfReader(filepath)
    except Exception as e:
        print(f"Error in PdfReader: \"{e}\" for \"{filepath}\"")
        return None

    if reader.is_encrypted:
        print(f"Warning: PDF is encrypted. \"{filepath}\"")
        return None
    return reader


def read_pdf_from_bytes(data: bytes) -> PdfReader:
    reader = PdfReader(BytesIO(data))
    if reader.is_encrypted:
        return None
    return reader


def apply_pdf_filters(config: dict, context: dict) -> dict:
    context['ret_pdf_keyword_matched'] = False

    # input keywords to match
    keywords = config['keywords']
    pdf_reader = context['pdfreader']

    for page in pdf_reader.pages:
        text = page.extract_text()

        ### Matching
        for item in keywords:
            results = find_exact_word(text, item)
            context['ret_pdf_keyword_matched'] = bool(results)
            context['keyword_match'] = results
            if bool(results):
                return context

    return context


def verdict_pdf_filter_output(context: dict) -> bool:
    return bool(context.get('keyword_match'))


def apply_pdf_filters_as_attachment(config: dict, context: dict, pdf_reader: PdfReader) -> dict:
    ret_pdf_keyword_matched = False

    # input keywords to match
    keywords = config['keywords']

    for page in pdf_reader.pages:
        # Extra check voor inhoudsobject
        contents = page.get("/Contents")
        if isinstance(contents, NullObject):
            print(f"Warning: Pagina heeft geen inhoud, wordt overgeslagen.")
            continue

        # Checked
        try:
            text = page.extract_text()
        except Exception as e:
            print("Error: PDF problem on this page: {e}")
            continue

        ### Matching
        for item in keywords:
            keyword_match = find_exact_word(text, item)
            if bool(keyword_match):
                return keyword_match

    return None
