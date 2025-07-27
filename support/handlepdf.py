import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

import asyncio
import pdfplumber
from io import BytesIO

from support.filter_support import apply_filter_on_fulltext_by_keywords
from support.logging import write_log


def read_pdf_from_file_to_text(filepath: str) -> str:
    with open(filepath, "rb") as f:
        data = f.read()

    return read_pdf_from_bytes_to_text(data)


# def read_pdf_from_bytes_to_text(config: dict, data: bytes) -> str:
#     try:
#         with pdfplumber.open(BytesIO(data)) as pdf:
#             all_text = "\n".join(filter(None, (p.extract_text() for p in pdf.pages)))
#     except Exception as e:
#         write_log(config, f'Error in pdfplumber: {e}')
#         all_text = None

#     return all_text

async def read_pdf_from_bytes_to_text(config: dict, data: bytes) -> str:
    def _sync_read():
        try:
            with pdfplumber.open(BytesIO(data)) as pdf:
                return "\n".join(filter(None, (p.extract_text() for p in pdf.pages)))
        except Exception as e:
            write_log(config, f'Error in pdfplumber: {e}')
            return None

    return await asyncio.to_thread(_sync_read)


def apply_pdf_filters(config: dict, context: dict) -> dict:
    context['ret_pdf_keyword_matched'] = False
    pdf_text: str = context['pdf']

    results = apply_filter_on_fulltext_by_keywords(config['filter']['keywords']['list_of_keywords'], pdf_text)
    context['keyword_match'] = results
    context['ret_pdf_keyword_matched'] = bool(results)

    return context


def verdict_pdf_filter_output(context: dict) -> bool:
    return bool(context.get('keyword_match'))
