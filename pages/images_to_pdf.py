import io

import streamlit as st
from PIL import Image


def render():
    st.header("Images to PDF")

    if "img2pdf_items" not in st.session_state:
        st.session_state.img2pdf_items = []  # [{"name": str, "data": bytes}]
    if "img2pdf_converted" not in st.session_state:
        st.session_state.img2pdf_converted = None  # bytes | None

    uploads = st.file_uploader(
        "Drop images here or click to browse",
        type=["png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploads is not None:
        incoming = {f.name for f in uploads}
        stored   = {item["name"] for item in st.session_state.img2pdf_items}
        if incoming != stored:
            st.session_state.img2pdf_items = [
                {"name": f.name, "data": f.read()} for f in uploads
            ]
            st.session_state.img2pdf_converted = None

    items = st.session_state.img2pdf_items

    if items:
        n = len(items)

        st.markdown(
            f"**{n} image{'s' if n > 1 else ''}** · "
            "top row = page 1 &nbsp;·&nbsp; use ↑ ↓ to reorder",
            unsafe_allow_html=True,
        )
        st.write("")

        for i, item in enumerate(items):
            img = Image.open(io.BytesIO(item["data"]))
            thumb = img.copy()
            thumb.thumbnail((72, 72))

            badge, thumb_col, info_col, up_col, dn_col = st.columns(
                [0.4, 0.9, 6, 0.55, 0.55], vertical_alignment="center"
            )

            badge.markdown(
                f"<div style='font-size:1.6rem;font-weight:700;"
                f"color:#555;text-align:center;line-height:1'>{i + 1}</div>",
                unsafe_allow_html=True,
            )
            thumb_col.image(thumb, width=56)
            info_col.markdown(
                f"**{item['name']}**  \n"
                f"<span style='color:#888;font-size:0.82rem'>"
                f"{img.width} × {img.height} px &nbsp;·&nbsp; "
                f"{len(item['data']) / 1024:.0f} KB</span>",
                unsafe_allow_html=True,
            )

            if up_col.button("↑", key=f"up_{i}", disabled=(i == 0), use_container_width=True):
                items[i], items[i - 1] = items[i - 1], items[i]
                st.session_state.img2pdf_converted = None
                st.rerun()
            if dn_col.button("↓", key=f"dn_{i}", disabled=(i == n - 1), use_container_width=True):
                items[i], items[i + 1] = items[i + 1], items[i]
                st.session_state.img2pdf_converted = None
                st.rerun()

        st.write("")
        st.divider()
        left, right = st.columns([3, 2])
        out_name = left.text_input(
            "Output filename",
            value="output.pdf",
            label_visibility="collapsed",
            placeholder="output.pdf",
        )
        convert_clicked = right.button(
            "Convert to PDF  →", type="primary", use_container_width=True
        )

        if convert_clicked:
            with st.spinner(f"Merging {n} image{'s' if n > 1 else ''}…"):
                pil_images = [
                    Image.open(io.BytesIO(item["data"])).convert("RGB")
                    for item in items
                ]
                buf = io.BytesIO()
                pil_images[0].save(
                    buf, format="PDF", save_all=True, append_images=pil_images[1:]
                )
                st.session_state.img2pdf_converted = buf.getvalue()

        if st.session_state.img2pdf_converted:
            fn = out_name if out_name.lower().endswith(".pdf") else out_name + ".pdf"
            st.success(f"Ready — {n}-page PDF")
            st.download_button(
                "⬇️  Download PDF",
                st.session_state.img2pdf_converted,
                fn,
                "application/pdf",
                use_container_width=True,
            )
