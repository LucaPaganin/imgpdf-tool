import io

import fitz  # PyMuPDF
import streamlit as st

from core.pdf_utils import open_pdf


def render():
    st.header("🔓 Unlock PDF")
    st.caption("Remove password protection from a PDF.")

    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    password = st.text_input("Current password", type="password")

    if upload:
        if st.button("Unlock", type="primary", use_container_width=True):
            doc = open_pdf(upload, password)
            if doc:
                if not upload.name.endswith(".pdf"):
                    st.error("Not a PDF file.")
                else:
                    buf = io.BytesIO()
                    doc.save(buf, encryption=fitz.PDF_ENCRYPT_NONE)
                    base = upload.name.rsplit(".", 1)[0]
                    st.success("✅ Password removed.")
                    st.download_button(
                        "⬇️ Download Unlocked PDF",
                        buf.getvalue(),
                        f"{base}_unlocked.pdf",
                        "application/pdf",
                        use_container_width=True,
                    )

render()
