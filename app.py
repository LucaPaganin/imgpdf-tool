import streamlit as st

st.set_page_config(
    page_title="ImgPDF Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIVACY_DISCLAIMER = (
    "**PRIVACY DISCLAIMER**: All data you upload here are not stored by the developer, "
    "and the code is open source on GitHub. Visit [the repository](https://github.com/LucaPaganin/imgpdf-tool) and read README.md "
    "to review the code."
)

pg = st.navigation([
    st.Page("pages/images_to_pdf.py", title="Images → PDF", icon="🖼️"),
    st.Page("pages/pdf_to_images.py", title="PDF → Images", icon="📄"),
    st.Page("pages/merge_pdfs.py",    title="Merge PDFs",   icon="🔗"),
    st.Page("pages/split_pdf.py",     title="Split PDF",    icon="✂️"),
    st.Page("pages/compress_pdf.py",  title="Compress PDF", icon="🗜️"),
    st.Page("pages/rotate_pdf.py",    title="Rotate PDF",   icon="🔄"),
    st.Page("pages/watermark.py",     title="Watermark",    icon="💧"),
    st.Page("pages/page_numbers.py",  title="Page Numbers", icon="🔢"),
    st.Page("pages/protect_pdf.py",   title="Protect PDF",  icon="🔒"),
    st.Page("pages/unlock_pdf.py",    title="Unlock PDF",   icon="🔓"),
    st.Page("pages/organize_pdf.py",  title="Organize PDF", icon="📋"),
])

with st.sidebar:
    st.markdown("## 📄 ImgPDF Tool")
    st.caption("All-in-one PDF & image toolkit")
    st.markdown(PRIVACY_DISCLAIMER)
    st.divider()

pg.run()
