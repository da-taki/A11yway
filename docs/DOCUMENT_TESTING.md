# Document Testing

`--document` inspects local `.pdf`, `.docx`, and `.pptx` files.

PDF checks inspect tagging metadata, title, declared language, encryption, page count, and extractable text. DOCX checks inspect title metadata, heading styles, skipped headings, layout paragraphs, simple table evidence, and image-alt metadata when exposed. PPTX checks inspect slide titles, duplicate titles, and picture/title review evidence.

These checks do not claim PDF/UA, WCAG conformance, or full Office accessibility conformance. Reading order remains manual-review evidence unless a format exposes deterministic structure.
