import streamlit as st

from core.pdf_utils import doc_to_bytes, dl_pdf, open_pdf


def render():
    st.header("🗜️ Compress PDF")
    st.caption("Reduce PDF file size by removing redundancies and re-compressing streams.")

    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    password = st.text_input("Password (if protected)", type="password")

    if upload:
        original_size = upload.size
        doc = open_pdf(upload, password)
        if doc:
            level = st.select_slider(
                "Compression level",
                options=["Light", "Balanced", "Aggressive"],
                value="Balanced",
            )
            garbage = {"Light": 1, "Balanced": 3, "Aggressive": 4}[level]
            clean = level == "Aggressive"

            if st.button("Compress", type="primary", use_container_width=True):
                with st.spinner("Compressing…"):
                    data = doc_to_bytes(doc, deflate=True, deflate_images=True, garbage=garbage, clean=clean)

                ratio = (1 - len(data) / original_size) * 100
                col1, col2, col3 = st.columns(3)
                col1.metric("Original", f"{original_size / 1024:.1f} KB")
                col2.metric("Compressed", f"{len(data) / 1024:.1f} KB")
                col3.metric("Reduction", f"{ratio:.1f}%", delta=f"-{ratio:.1f}%")

                base = upload.name.rsplit(".", 1)[0]
                dl_pdf(data, f"{base}_compressed.pdf")
