import fitz  # PyMuPDF
import streamlit as st
from PIL import Image

from core.pdf_utils import doc_to_bytes


def render():
    st.header("📋 Organize PDF")

    if "org_key" not in st.session_state:
        st.session_state.org_key    = ""
    if "org_data" not in st.session_state:
        st.session_state.org_data   = None
    if "org_pages" not in st.session_state:
        st.session_state.org_pages  = []
    if "org_result" not in st.session_state:
        st.session_state.org_result = None

    upload   = st.file_uploader("Drop a PDF here or click to browse", type=["pdf"], label_visibility="collapsed")
    password = st.text_input("Password (if protected)", type="password")

    if upload is not None:
        file_key = upload.name + str(upload.size)
        if file_key != st.session_state.org_key:
            raw = upload.read()
            tmp = fitz.open(stream=raw, filetype="pdf")
            if tmp.needs_pass and not tmp.authenticate(password):
                st.error("❌ Wrong password.")
            else:
                MAX_THUMBS = 60
                mat = fitz.Matrix(0.22, 0.22)   # ~16 DPI — fast & recognisable
                page_list = []
                with st.spinner(f"Loading {len(tmp)} pages…"):
                    for i in range(len(tmp)):
                        if i < MAX_THUMBS:
                            pix   = tmp[i].get_pixmap(matrix=mat, alpha=False)
                            thumb = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        else:
                            thumb = None
                        page_list.append({"orig": i, "thumb": thumb, "deleted": False})
                st.session_state.org_key    = file_key
                st.session_state.org_data   = raw
                st.session_state.org_pages  = page_list
                st.session_state.org_result = None

    pages = st.session_state.org_pages

    if pages:
        total         = len(pages)
        kept          = sum(1 for p in pages if not p["deleted"])
        deleted_count = total - kept

        kept_label = f"<span style='color:#2a7'><b>{kept}</b> kept</span>"
        del_label  = (
            f" &nbsp;·&nbsp; <span style='color:#e55'><b>{deleted_count}</b> removed</span>"
            if deleted_count else ""
        )
        hint_label = "&nbsp;·&nbsp; <span style='color:#aaa;font-size:0.82rem'>↑ ↓ reorder &nbsp; ✕ remove &nbsp; ↺ restore</span>"
        st.markdown(
            f"**{total} pages** &nbsp;·&nbsp; {kept_label}{del_label}{hint_label}",
            unsafe_allow_html=True,
        )
        st.write("")

        pos_counter = 0
        for i, p in enumerate(pages):
            is_del = p["deleted"]
            if not is_del:
                pos_counter += 1
                badge_val = str(pos_counter)
                badge_style = "font-size:1.35rem;font-weight:700;color:#555;text-align:center;line-height:1"
            else:
                badge_val   = "—"
                badge_style = "font-size:1.2rem;color:#ccc;text-align:center"

            badge, thumb_col, info_col, up_col, dn_col, action_col = st.columns(
                [0.35, 0.6, 4.5, 0.5, 0.5, 0.6], vertical_alignment="center"
            )

            badge.markdown(
                f"<div style='{badge_style}'>{badge_val}</div>",
                unsafe_allow_html=True,
            )

            if p["thumb"] is not None:
                img = p["thumb"].convert("L").convert("RGB") if is_del else p["thumb"]
                thumb_col.image(img, width=40)
            else:
                thumb_col.markdown(
                    "<div style='width:40px;height:52px;background:#f0f0f0;border-radius:3px;"
                    "display:flex;align-items:center;justify-content:center;"
                    "color:#bbb;font-size:0.65rem;text-align:center'>p.</div>",
                    unsafe_allow_html=True,
                )

            if is_del:
                info_col.markdown(
                    f"<span style='color:#ccc;text-decoration:line-through'>Page {p['orig'] + 1}</span>",
                    unsafe_allow_html=True,
                )
            else:
                info_col.markdown(
                    f"<span style='color:#444'>Page {p['orig'] + 1}</span>",
                    unsafe_allow_html=True,
                )

            if up_col.button("↑", key=f"oup_{i}", disabled=(i == 0 or is_del), use_container_width=True):
                pages[i], pages[i - 1] = pages[i - 1], pages[i]
                st.session_state.org_result = None
                st.rerun()
            if dn_col.button("↓", key=f"odn_{i}", disabled=(i == total - 1 or is_del), use_container_width=True):
                pages[i], pages[i + 1] = pages[i + 1], pages[i]
                st.session_state.org_result = None
                st.rerun()

            if is_del:
                if action_col.button("↺", key=f"ors_{i}", use_container_width=True, help="Restore this page"):
                    pages[i]["deleted"] = False
                    st.session_state.org_result = None
                    st.rerun()
            else:
                if action_col.button("✕", key=f"odl_{i}", use_container_width=True, help="Remove this page"):
                    pages[i]["deleted"] = True
                    st.session_state.org_result = None
                    st.rerun()

        st.write("")
        st.divider()
        _, right = st.columns([3, 2])
        if right.button("Apply  →", type="primary", use_container_width=True, disabled=(kept == 0)):
            keep_order = [p["orig"] for p in pages if not p["deleted"]]
            with st.spinner(f"Building {kept}-page PDF…"):
                src = fitz.open(stream=st.session_state.org_data, filetype="pdf")
                if src.needs_pass:
                    src.authenticate(password)
                out = fitz.open()
                for idx in keep_order:
                    out.insert_pdf(src, from_page=idx, to_page=idx)
                st.session_state.org_result = doc_to_bytes(out)

        if st.session_state.org_result:
            base = upload.name.rsplit(".", 1)[0] if upload else "document"
            st.success(f"Ready — {kept}-page PDF")
            st.download_button(
                "⬇️  Download PDF",
                st.session_state.org_result,
                f"{base}_organized.pdf",
                "application/pdf",
                use_container_width=True,
            )

render()
