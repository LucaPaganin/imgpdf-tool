import io
import zipfile

import fitz  # PyMuPDF
import streamlit as st

from core.pdf_utils import doc_to_bytes


def render():
    st.header("Split PDF")

    if "split_key" not in st.session_state:
        st.session_state.split_key   = ""
    if "split_data" not in st.session_state:
        st.session_state.split_data  = None
    if "split_total" not in st.session_state:
        st.session_state.split_total = 0
    if "split_parts" not in st.session_state:
        st.session_state.split_parts = []
    if "split_result" not in st.session_state:
        st.session_state.split_result = None   # ("single"|"zip", bytes, filename)

    upload   = st.file_uploader("Drop a PDF here or click to browse", type=["pdf"], label_visibility="collapsed")
    password = st.text_input("Password (if protected)", type="password")

    if upload is not None:
        file_key = upload.name + str(upload.size)
        if file_key != st.session_state.split_key:
            raw = upload.read()
            tmp = fitz.open(stream=raw, filetype="pdf")
            if tmp.needs_pass and not tmp.authenticate(password):
                st.error("❌ Wrong password.")
            else:
                st.session_state.split_key   = file_key
                st.session_state.split_data  = raw
                st.session_state.split_total = len(tmp)
                st.session_state.split_parts = [[1, len(tmp)]]
                st.session_state.split_result = None

    if st.session_state.split_data:
        total = st.session_state.split_total
        base  = upload.name.rsplit(".", 1)[0] if upload else "document"

        st.markdown(f"**{total} pages**")
        st.write("")

        mode = st.radio(
            "Split mode",
            ["Every page", "Custom ranges", "Every N pages"],
            horizontal=True,
            label_visibility="collapsed",
        )

        ranges_0idx: list[list[int]] = []

        if mode == "Every page":
            ranges_0idx = [[i, i] for i in range(total)]
            st.info(f"Will create **{total}** individual page PDF{'s' if total > 1 else ''}.")

        elif mode == "Custom ranges":
            parts = st.session_state.split_parts

            for i, r in enumerate(parts):
                c_lbl, c_from, c_dash, c_to, c_rm = st.columns(
                    [1.1, 2, 0.35, 2, 1], vertical_alignment="center"
                )
                c_lbl.markdown(f"**Part {i + 1}**")
                r[0] = c_from.number_input(
                    "From", min_value=1, max_value=total, value=int(r[0]),
                    key=f"sp_f{i}", label_visibility="collapsed",
                )
                c_dash.markdown(
                    "<div style='text-align:center;padding-top:4px;color:#888'>–</div>",
                    unsafe_allow_html=True,
                )
                r[1] = c_to.number_input(
                    "To", min_value=1, max_value=total, value=int(r[1]),
                    key=f"sp_t{i}", label_visibility="collapsed",
                )
                if c_rm.button("Remove", key=f"sp_rm{i}", use_container_width=True):
                    parts.pop(i)
                    st.session_state.split_result = None
                    st.rerun()
                if r[0] > r[1]:
                    st.warning(f"Part {i + 1}: start page ({r[0]}) is after end page ({r[1]}).")

            col_add, _ = st.columns([1.5, 5])
            if col_add.button("＋ Add part", use_container_width=True):
                last = parts[-1][1] if parts else 0
                parts.append([min(last + 1, total), total])
                st.session_state.split_result = None
                st.rerun()

            valid_parts = [r for r in parts if r[0] <= r[1]]
            if valid_parts:
                covered = sum(r[1] - r[0] + 1 for r in valid_parts)
                st.caption(
                    f"{len(valid_parts)} file{'s' if len(valid_parts) > 1 else ''} &nbsp;·&nbsp; "
                    f"{covered} of {total} pages covered"
                )
                ranges_0idx = [[r[0] - 1, r[1] - 1] for r in valid_parts]

        else:
            n = st.number_input("Pages per file", min_value=1, max_value=total, value=min(5, total))
            chunks = list(range(0, total, n))
            ranges_0idx = [[c, min(c + n - 1, total - 1)] for c in chunks]
            st.info(
                f"Will create **{len(ranges_0idx)}** file{'s' if len(ranges_0idx) > 1 else ''} "
                f"of up to {n} page{'s' if n > 1 else ''} each."
            )

        st.write("")
        st.divider()
        _, right = st.columns([3, 2])
        if right.button("Split  →", type="primary", use_container_width=True) and ranges_0idx:
            with st.spinner(f"Splitting into {len(ranges_0idx)} file(s)…"):
                doc = fitz.open(stream=st.session_state.split_data, filetype="pdf")
                if doc.needs_pass:
                    doc.authenticate(password)
                if len(ranges_0idx) == 1:
                    out = fitz.open()
                    out.insert_pdf(doc, from_page=ranges_0idx[0][0], to_page=ranges_0idx[0][1])
                    st.session_state.split_result = ("single", doc_to_bytes(out), f"{base}_part1.pdf")
                else:
                    zb = io.BytesIO()
                    with zipfile.ZipFile(zb, "w", zipfile.ZIP_DEFLATED) as zf:
                        for idx, r in enumerate(ranges_0idx):
                            out = fitz.open()
                            out.insert_pdf(doc, from_page=r[0], to_page=r[1])
                            zf.writestr(f"{base}_part{idx + 1:03d}.pdf", doc_to_bytes(out))
                    st.session_state.split_result = ("zip", zb.getvalue(), f"{base}_split.zip")

        if st.session_state.split_result:
            kind, data_out, fname = st.session_state.split_result
            mime  = "application/pdf" if kind == "single" else "application/zip"
            label = "⬇️  Download PDF"  if kind == "single" else "⬇️  Download ZIP"
            n_files = len(ranges_0idx) if ranges_0idx else "?"
            st.success(f"Ready — {n_files} file{'s' if n_files != 1 else ''}")
            st.download_button(label, data_out, fname, mime, use_container_width=True)
