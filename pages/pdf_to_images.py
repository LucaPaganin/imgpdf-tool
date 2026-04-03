import io
import zipfile

import fitz  # PyMuPDF
import streamlit as st
from PIL import Image

from core.pdf_utils import open_pdf, parse_ranges


def render():
    st.header("📄 PDF → Images")
    st.caption("Extract each page as an image and download them as a ZIP.")

    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    password = st.text_input("Password (if protected)", type="password")

    if upload:
        doc = open_pdf(upload, password)
        if doc:
            total = len(doc)
            st.info(f"📑 {total} page(s) detected.")

            c1, c2, c3 = st.columns(3)
            fmt = c1.selectbox("Image format", ["PNG", "JPEG", "WEBP"])
            dpi = c2.slider("DPI", 72, 300, 150, 12)
            page_range = c3.text_input("Pages (e.g. 1-3, 5)", placeholder=f"1-{total} (all)")

            if st.button("Convert", type="primary", use_container_width=True):
                pages_idx = parse_ranges(page_range, total) if page_range.strip() else list(range(total))
                if pages_idx is not None:
                    with st.spinner("Rendering pages…"):
                        zoom = dpi / 72
                        mat = fitz.Matrix(zoom, zoom)
                        zip_buf = io.BytesIO()
                        previews: list[tuple[str, Image.Image]] = []

                        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                            for idx in pages_idx:
                                pix = doc[idx].get_pixmap(matrix=mat, alpha=False)
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                img_buf = io.BytesIO()
                                img.save(img_buf, format=fmt)
                                fname = f"page_{idx + 1:03d}.{fmt.lower()}"
                                zf.writestr(fname, img_buf.getvalue())
                                if len(previews) < 6:
                                    previews.append((fname, img))

                        zip_buf.seek(0)

                    st.success(f"✅ {len(pages_idx)} page(s) converted.")
                    base = upload.name.rsplit(".", 1)[0]
                    st.download_button(
                        "⬇️ Download ZIP",
                        zip_buf,
                        f"{base}_images.zip",
                        "application/zip",
                        use_container_width=True,
                    )

                    if previews:
                        st.subheader("Preview")
                        cols = st.columns(min(len(previews), 3))
                        for i, (name, img) in enumerate(previews):
                            cols[i % 3].image(img, caption=name, use_container_width=True)

render()
