import io
import re

import fitz  # PyMuPDF
import streamlit as st
from PIL import Image


def doc_to_bytes(doc: fitz.Document, **kw) -> bytes:
    buf = io.BytesIO()
    doc.save(buf, **kw)
    return buf.getvalue()


def dl_pdf(data: bytes, filename: str, label: str = "⬇️ Download PDF"):
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    st.download_button(label, data, filename, "application/pdf", use_container_width=True)


def open_pdf(file, password: str = "") -> fitz.Document | None:
    """Open a PDF from a Streamlit UploadedFile, optionally authenticating."""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    if doc.needs_pass:
        if not doc.authenticate(password):
            st.error("❌ Wrong password.")
            return None
    return doc


def parse_ranges(text: str, total: int) -> list[int] | None:
    """
    Parse a page-range string like '1, 3, 5-7' into a 0-indexed list.
    Returns None and emits an st.error on bad input.
    """
    pages: list[int] = []
    for part in re.split(r"[,\s]+", text.strip()):
        if not part:
            continue
        m = re.fullmatch(r"(\d+)-(\d+)", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a < 1 or b > total or a > b:
                st.error(f"Invalid range '{part}' (document has {total} pages).")
                return None
            pages.extend(range(a - 1, b))
        elif re.fullmatch(r"\d+", part):
            n = int(part)
            if n < 1 or n > total:
                st.error(f"Page {n} is out of range (document has {total} pages).")
                return None
            pages.append(n - 1)
        else:
            st.error(f"Cannot parse '{part}'.")
            return None
    if not pages:
        st.error("No pages found in the given range.")
        return None
    return pages


def pdf_thumbnails(doc: fitz.Document, max_pages: int = 20, dpi: int = 72) -> list[Image.Image]:
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    thumbs = []
    for i in range(min(len(doc), max_pages)):
        pix = doc[i].get_pixmap(matrix=mat, alpha=False)
        thumbs.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    return thumbs


def show_thumbnails(thumbs: list[Image.Image], captions: list[str], cols: int = 5):
    columns = st.columns(cols)
    for i, (img, cap) in enumerate(zip(thumbs, captions)):
        columns[i % cols].image(img, caption=cap, use_container_width=True)
