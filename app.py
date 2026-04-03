import streamlit as st

from pages import (
    compress_pdf,
    images_to_pdf,
    merge_pdfs,
    organize_pdf,
    page_numbers,
    pdf_to_images,
    protect_pdf,
    rotate_pdf,
    split_pdf,
    unlock_pdf,
    watermark,
)

st.set_page_config(
    page_title="ImgPDF Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "🖼️  Images → PDF": images_to_pdf,
    "📄  PDF → Images": pdf_to_images,
    "🔗  Merge PDFs":   merge_pdfs,
    "✂️  Split PDF":    split_pdf,
    "🗜️  Compress PDF": compress_pdf,
    "🔄  Rotate PDF":   rotate_pdf,
    "💧  Watermark":    watermark,
    "🔢  Page Numbers": page_numbers,
    "🔒  Protect PDF":  protect_pdf,
    "🔓  Unlock PDF":   unlock_pdf,
    "📋  Organize PDF": organize_pdf,
}

PRIVACY_DISCLAIMER = (
    "**PRIVACY DISCLAIMER**: All data you upload here are not stored by the developer, "
    "and the code is open source on GitHub. Visit [the repository](https://github.com/LucaPaganin/imgpdf-tool) and read README.md "
    "to review the code."
)


with st.sidebar:
    st.markdown("## 📄 ImgPDF Tool")
    st.caption("All-in-one PDF & image toolkit")
    st.markdown()
    st.divider()
    page = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")

PAGES[page].render()
