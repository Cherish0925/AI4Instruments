# Paper

**From Instruments4AI to AI4Instruments**

**Shuxing Yang** · Version 0.2.1 · October 2026

- [PDF](AI4Instruments.pdf): typeset A4 article.
- [HTML](AI4Instruments.html): self-contained article with embedded figures, navigation and responsive styling. Download and open in a browser to read offline.
- [Manuscript](manuscript.md): editable Markdown source.
- [References](references.json): verified primary-source bibliography.

Both published formats are generated from the same manuscript and reference list:

```bash
python -m pip install -r requirements-paper.txt
python scripts/build_paper.py
```

Run from the repository root. `--html-only` skips PDF generation and needs no third-party package. Figures are generated as vector graphics by the build script. Citation metadata is in [`CITATION.cff`](../CITATION.cff).
