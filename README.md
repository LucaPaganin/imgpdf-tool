# ImgPDF Tool

An all-in-one PDF and image toolkit that runs entirely in your browser — no account, no cloud upload, no data stored.

---

## For Users

### What it does

ImgPDF Tool is a free, open-source web app that lets you work with PDF files and images without installing any software. All processing happens on the server running the app — your files are never stored or shared.

### Features

| Tool | Description |
|------|-------------|
| **Images → PDF** | Combine multiple images into a single PDF. Drag to reorder before converting. |
| **PDF → Images** | Extract pages as PNG, JPEG, or WEBP images. Choose DPI and page range. Download as ZIP. |
| **Merge PDFs** | Combine multiple PDF files into one. Drag to set the order. |
| **Split PDF** | Split a PDF into individual pages, custom ranges, or fixed-size chunks. |
| **Compress PDF** | Reduce file size with Light, Balanced, or Aggressive compression. |
| **Rotate PDF** | Rotate all pages or a specific range by 90°, 180°, or 270°. |
| **Watermark** | Stamp a text watermark on every page. Control font size, opacity, angle, and color. |
| **Page Numbers** | Add page numbers at any corner or center. Customize format, start number, and font size. |
| **Protect PDF** | Encrypt a PDF with a password and restrict printing, copying, or editing. |
| **Unlock PDF** | Remove password protection from a PDF you already have the password for. |
| **Organize PDF** | Reorder and delete individual pages with a visual thumbnail editor. |

### Privacy

All files you upload are processed in memory and immediately discarded — nothing is written to disk or logged. The source code is fully open for inspection in this repository.

---

## For Developers

### Tech stack

- **[Streamlit](https://streamlit.io/)** — UI framework
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** (`fitz`) — PDF rendering and manipulation
- **[Pillow](https://pillow.readthedocs.io/)** — image processing
- **[uv](https://docs.astral.sh/uv/)** — package and project manager (recommended)

### Requirements

- Python 3.13+
- uv (or pip)

### Getting started

**With uv (recommended):**

```bash
git clone https://github.com/LucaPaganin/imgpdf-tool.git
cd imgpdf-tool
uv run streamlit run app.py
```

**With pip:**

```bash
git clone https://github.com/LucaPaganin/imgpdf-tool.git
cd imgpdf-tool
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Project structure

```
imgpdf-tool/
├── app.py              # Entry point: page config, sidebar, routing
├── core/
│   └── pdf_utils.py    # Shared helpers: open_pdf, doc_to_bytes, parse_ranges, etc.
└── pages/
    ├── images_to_pdf.py
    ├── pdf_to_images.py
    ├── merge_pdfs.py
    ├── split_pdf.py
    ├── compress_pdf.py
    ├── rotate_pdf.py
    ├── watermark.py
    ├── page_numbers.py
    ├── protect_pdf.py
    ├── unlock_pdf.py
    └── organize_pdf.py
```

Each file in `pages/` exposes a single `render()` function. `app.py` maps sidebar navigation entries to modules and calls `render()` on the selected one.

### Adding a new page

1. Create `pages/my_feature.py` with a `render()` function.
2. Import it in `app.py` and add an entry to the `PAGES` dict.

That's it — no registration, no framework magic.

### Dependencies

Declared in `pyproject.toml`. Pin versions with `uv lock` and commit `uv.lock` for reproducible installs.

```
streamlit>=1.36.0
pymupdf>=1.24.0
pillow>=10.0.0
```

### Contributing

Bug reports and pull requests are welcome. Please open an issue first for significant changes so we can discuss the approach.
