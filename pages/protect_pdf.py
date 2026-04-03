import io

import fitz  # PyMuPDF
import streamlit as st

from core.pdf_utils import open_pdf


def render():
    st.header("🔒 Protect PDF")
    st.caption("Encrypt a PDF with a password.")

    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    current_pw = st.text_input("Current password (if already protected)", type="password")

    if upload:
        doc = open_pdf(upload, current_pw)
        if doc:
            c1, c2 = st.columns(2)
            new_pw = c1.text_input("New password", type="password")
            confirm_pw = c2.text_input("Confirm password", type="password")

            st.caption("Permissions to restrict:")
            col_a, col_b, col_c = st.columns(3)
            allow_print = col_a.checkbox("Allow printing", value=True)
            allow_copy = col_b.checkbox("Allow copying text", value=False)
            allow_edit = col_c.checkbox("Allow editing", value=False)

            if st.button("Protect", type="primary", use_container_width=True):
                if not new_pw:
                    st.error("Please enter a password.")
                elif new_pw != confirm_pw:
                    st.error("Passwords do not match.")
                else:
                    perm = fitz.PDF_PERM_ACCESSIBILITY
                    if allow_print:
                        perm |= fitz.PDF_PERM_PRINT
                    if allow_copy:
                        perm |= fitz.PDF_PERM_COPY
                    if allow_edit:
                        perm |= fitz.PDF_PERM_MODIFY | fitz.PDF_PERM_ANNOTATE

                    enc = fitz.PDF_ENCRYPT_AES_256
                    buf = io.BytesIO()
                    doc.save(buf, encryption=enc, user_pw=new_pw, owner_pw=new_pw + "_owner", permissions=perm)
                    base = upload.name.rsplit(".", 1)[0]
                    st.success("✅ PDF protected.")
                    st.download_button(
                        "⬇️ Download Protected PDF",
                        buf.getvalue(),
                        f"{base}_protected.pdf",
                        "application/pdf",
                        use_container_width=True,
                    )

render()
