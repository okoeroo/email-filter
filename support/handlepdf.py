from PyPDF2 import PdfReader
from PyPDF2.generic import NullObject
from io import BytesIO
from support.filter_support import apply_filter_on_fulltext_by_keywords


def read_pdf_from_file_to_text(filepath: str) -> str:
    with open(filepath, "rb") as f:
        data = f.read()

    return read_pdf_from_bytes_to_text(data)


def read_pdf_from_bytes_to_text(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
    except Exception as e:
        print(f"Error in PdfReader: \"{e}\"")

    if reader.is_encrypted:
        return None

    # to full text
    elements = []

    for page in reader.pages:
        # Extra check voor inhoudsobject
        contents = page.get("/Contents")
        if isinstance(contents, NullObject):
            print(f"Warning: Pagina heeft geen inhoud, wordt overgeslagen.")
            continue

        # Checked
        try:
            elements.append(page.extract_text())
        except Exception as e:
            print(f"Error: PDF problem on this page: {e}")
            continue

    return "\n".join(elements)


def apply_pdf_filters(config: dict, context: dict) -> dict:
    context['ret_pdf_keyword_matched'] = False
    pdf_text: str = context['pdf']

    results = apply_filter_on_fulltext_by_keywords(config['keywords'], pdf_text)
    context['keyword_match'] = results
    context['ret_pdf_keyword_matched'] = bool(results)

    return context


def verdict_pdf_filter_output(context: dict) -> bool:
    return bool(context.get('keyword_match'))
