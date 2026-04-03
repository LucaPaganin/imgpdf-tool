import fitz  # PyMuPDF
import streamlit as st

from core.pdf_utils import doc_to_bytes, dl_pdf, open_pdf


def render():
    st.header("🔢 Page Numbers")
    st.caption("Add page numbers to every page.")

    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    password = st.text_input("Password (if protected)", type="password")

    if upload:
        doc = open_pdf(upload, password)
        if doc:
            c1, c2, c3 = st.columns(3)
            position = c1.selectbox("Position", ["Bottom Center", "Bottom Right", "Bottom Left", "Top Center", "Top Right", "Top Left"])
            start = c2.number_input("Start number", min_value=0, value=1)
            font_size = c3.slider("Font size", 6, 24, 10)

            prefix = st.text_input("Prefix / suffix (optional)", placeholder='e.g. "Page {n} of {total}"', value="{n}")
            st.caption("Use `{n}` for the current page number and `{total}` for total pages.")

            if st.button("Add Page Numbers", type="primary", use_container_width=True):
                with st.spinner("Numbering pages…"):
                    total = len(doc)
                    margin = 30
                    for i, pg in enumerate(doc):
                        r = pg.rect
                        label = prefix.replace("{n}", str(start + i)).replace("{total}", str(total))

                        if "Bottom" in position:
                            y = r.height - margin
                        else:
                            y = margin + font_size

                        if "Center" in position:
                            x = r.width / 2 - len(label) * font_size * 0.25
                        elif "Right" in position:
                            x = r.width - margin - len(label) * font_size * 0.5
                        else:
                            x = margin

                        pg.insert_text(
                            fitz.Point(x, y),
                            label,
                            fontsize=font_size,
                            color=(0, 0, 0),
                            overlay=True,
                        )

                base = upload.name.rsplit(".", 1)[0]
                st.success(f"✅ Page numbers added to {total} page(s).")
                dl_pdf(doc_to_bytes(doc), f"{base}_numbered.pdf")
