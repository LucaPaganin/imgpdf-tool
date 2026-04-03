import fitz  # PyMuPDF
import streamlit as st

from core.pdf_utils import doc_to_bytes


def render():
    st.header("🔗 Merge PDFs")

    if "merge_items" not in st.session_state:
        st.session_state.merge_items = []   # [{"name", "data", "pages", "size"}]
    if "merge_result" not in st.session_state:
        st.session_state.merge_result = None

    uploads = st.file_uploader(
        "Drop PDF files here or click to browse",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploads is not None:
        incoming = {f.name for f in uploads}
        stored   = {it["name"] for it in st.session_state.merge_items}
        if incoming != stored:
            items = []
            for f in uploads:
                data = f.read()
                try:
                    d = fitz.open(stream=data, filetype="pdf")
                    pg_count = len(d)
                except Exception:
                    pg_count = 0
                items.append({"name": f.name, "data": data, "pages": pg_count, "size": len(data)})
            st.session_state.merge_items  = items
            st.session_state.merge_result = None

    items = st.session_state.merge_items

    if items:
        n            = len(items)
        total_pages  = sum(it["pages"] for it in items)

        st.markdown(
            f"**{n} file{'s' if n > 1 else ''}** &nbsp;·&nbsp; {total_pages} total pages &nbsp;·&nbsp; "
            "top row = first in output",
            unsafe_allow_html=True,
        )
        st.write("")

        for i, it in enumerate(items):
            badge, info_col, meta_col, up_col, dn_col = st.columns(
                [0.4, 5, 2.2, 0.55, 0.55], vertical_alignment="center"
            )
            badge.markdown(
                f"<div style='font-size:1.6rem;font-weight:700;color:#555;"
                f"text-align:center;line-height:1'>{i + 1}</div>",
                unsafe_allow_html=True,
            )
            info_col.markdown(f"**{it['name']}**")
            meta_col.markdown(
                f"<span style='color:#888;font-size:0.82rem'>"
                f"{it['pages']} pages &nbsp;·&nbsp; {it['size'] / 1024:.0f} KB</span>",
                unsafe_allow_html=True,
            )
            if up_col.button("↑", key=f"mup_{i}", disabled=(i == 0), use_container_width=True):
                items[i], items[i - 1] = items[i - 1], items[i]
                st.session_state.merge_result = None
                st.rerun()
            if dn_col.button("↓", key=f"mdn_{i}", disabled=(i == n - 1), use_container_width=True):
                items[i], items[i + 1] = items[i + 1], items[i]
                st.session_state.merge_result = None
                st.rerun()

        st.write("")
        st.divider()
        left, right = st.columns([3, 2])
        out_name = left.text_input(
            "Output filename",
            value="merged.pdf",
            label_visibility="collapsed",
            placeholder="merged.pdf",
        )
        if right.button("Merge  →", type="primary", use_container_width=True):
            with st.spinner(f"Merging {n} PDFs…"):
                merged = fitz.open()
                for it in items:
                    d = fitz.open(stream=it["data"], filetype="pdf")
                    merged.insert_pdf(d)
                st.session_state.merge_result = doc_to_bytes(merged)

        if st.session_state.merge_result:
            fn = out_name if out_name.lower().endswith(".pdf") else out_name + ".pdf"
            st.success(f"Ready — {total_pages}-page PDF")
            st.download_button(
                "⬇️  Download PDF",
                st.session_state.merge_result,
                fn,
                "application/pdf",
                use_container_width=True,
            )

render()
