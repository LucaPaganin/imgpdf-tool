import streamlit as st

from core.pdf_utils import doc_to_bytes, dl_pdf, open_pdf, parse_ranges


def render():
    st.header("🔄 Rotate PDF")
    st.caption("Rotate all pages or a specific range.")

    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    password = st.text_input("Password (if protected)", type="password")

    if upload:
        doc = open_pdf(upload, password)
        if doc:
            total = len(doc)
            st.info(f"📑 {total} page(s) detected.")

            c1, c2 = st.columns(2)
            angle = c1.select_slider("Rotation", options=[90, 180, 270], value=90)
            page_range = c2.text_input("Pages", placeholder=f"1-{total} (all)")

            if st.button("Rotate", type="primary", use_container_width=True):
                pages_idx = parse_ranges(page_range, total) if page_range.strip() else list(range(total))
                if pages_idx is not None:
                    with st.spinner("Rotating…"):
                        for i in pages_idx:
                            doc[i].set_rotation((doc[i].rotation + angle) % 360)
                    base = upload.name.rsplit(".", 1)[0]
                    st.success(f"✅ Rotated {len(pages_idx)} page(s) by {angle}°.")
                    dl_pdf(doc_to_bytes(doc), f"{base}_rotated.pdf")

render()
