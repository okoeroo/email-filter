import olefile
import zipfile
from docx import Document
from io import BytesIO
from support.filter_support import apply_filter_on_fulltext_by_keywords


def read_olefile_as_text(data: bytes) -> str:
    try:
        ole = olefile.OleFileIO(BytesIO(data))
        text_parts = []
        for entry in ole.listdir():
            name = '/'.join(entry)
            if "text" in name.lower() or "body" in name.lower() or "content" in name.lower():
                try:
                    with ole.openstream(entry) as stream:
                        data = stream.read()
                        try:
                            text = data.decode("utf-8")
                        except UnicodeDecodeError:
                            text = data.decode("latin1", errors="replace")
                        text_parts.append(f"--- {name} ---\n{text}")
                except Exception as e:
                    print(f"Fout bij {name}: {e}")
        return "\n\n".join(text_parts)
    except NotOleFileError as e:
        print(f"Not an OLE file: {e}")
        return None
    except Exception as e:
        print(f"Error in OLE: {e}")
        return None


def read_openxml_as_text(data: bytes) -> str:
    try:
        text_parts = []
        with zipfile.ZipFile(BytesIO(data)) as zipf:
            zf_list = zipf.namelist()
            for filename in zf_list:
                with zipf.open(filename) as f:
                    text_parts.append(f.read().decode('utf-8', errors='ignore'))
        return "\n".join(text_parts)
    except Exception as e:
        return None


def read_worddoc_as_text(data: bytes) -> str:
    try:
        docx = Document(BytesIO(data))
        full_text = "".join(para.text for para in docx.paragraphs)
        return full_text

    except ValueError as e:
        return None

    except Exception as e:
        print(f"Error: failure in docx conversion. {e}, trying openxml.")
        return None


def read_docx_from_bytes_to_text(data: bytes) -> str:
    full_text = read_worddoc_as_text(data)
    if full_text:
        return full_text

    full_text = read_openxml_as_text(data)
    if full_text:
        return full_text

    full_text = read_olefile_as_text(data)
    if full_text:
        return full_text

    return None


# def read_docx(filepath: str) -> str:
#     with open(filepath, "rb") as f:
#         raw_bytes = f.read()
#     return read_docx_from_bytes(raw_bytes)


# IMPORTANT: time is more complicated to judge. Hence, no timeframe matching is done here.
def apply_docx_filters(config: dict, context: dict) -> dict:
    doc_text: str = context['docx']
    context['ret_docx_keyword_matched'] = False

    results = apply_filter_on_fulltext_by_keywords(config['keywords'], doc_text)
    context['keyword_match'] = results
    context['ret_docx_keyword_matched'] = bool(results)

    return context


def verdict_docx_filter_output(context: dict) -> bool:
    return bool(context.get('keyword_match'))
