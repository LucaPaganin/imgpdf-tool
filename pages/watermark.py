import fitz  # PyMuPDF
import streamlit as st

from core.pdf_utils import doc_to_bytes, dl_pdf, open_pdf


def render():
    st.header("💧 Watermark")
    st.caption("Stamp a text watermark on every page.")

    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    password = st.text_input("Password (if protected)", type="password")

    if upload:
        doc = open_pdf(upload, password)
        if doc:
            c1, c2 = st.columns(2)
            wm_text = c1.text_input("Watermark text", value="CONFIDENTIAL")
            font_size = c2.slider("Font size", 12, 120, 60)

            c3, c4, c5 = st.columns(3)
            opacity = c3.slider("Opacity", 0.05, 1.0, 0.25, 0.05)
            angle = c4.select_slider("Angle", options=[0, 30, 45, 60, 90], value=45)
            color_choice = c5.selectbox("Color", ["Gray", "Black", "Red", "Blue"])
            color_map = {
                "Gray": (0.5, 0.5, 0.5),
                "Black": (0.0, 0.0, 0.0),
                "Red": (0.8, 0.0, 0.0),
                "Blue": (0.0, 0.0, 0.8),
            }
            color = color_map[color_choice]

            if st.button("Apply Watermark", type="primary", use_container_width=True) and wm_text.strip():
                with st.spinner("Stamping pages…"):
                    font = fitz.Font("helv")
                    for pg in doc:
                        rect = pg.rect
                        tw = fitz.TextWriter(rect, opacity=opacity, color=color)
                        tw.append(
                            fitz.Point(rect.width * 0.05, rect.height * 0.55),
                            wm_text,
                            font=font,
                            fontsize=font_size,
                        )
                        pivot = fitz.Point(rect.width / 2, rect.height / 2)
                        tw.write_text(pg, morph=(pivot, fitz.Matrix(angle)))

                base = upload.name.rsplit(".", 1)[0]
                st.success("✅ Watermark applied.")
                dl_pdf(doc_to_bytes(doc), f"{base}_watermarked.pdf")
