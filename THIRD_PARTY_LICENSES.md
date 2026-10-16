# Third-Party Licenses & Software Inventory

All third-party libraries, packages, and frameworks utilized in VeriDocs AI have been vetted for licensing compliance. Only permissive licenses (MIT, BSD-3-Clause, Apache-2.0, HPND) are permitted. Copyleft and AGPL libraries (e.g. PyMuPDF / fitz) are strictly excluded.

---

## Python Libraries (Backend & Evaluation)

| Name | Specified Version | License | Source Repository | Purpose / Reason Chosen |
|---|---|---|---|---|
| **Python** | 3.11.15 | PSF License | https://python.org | Runtime environment on macOS arm64 |
| **fastapi** | >=0.110.0 | MIT | https://github.com/tiangolo/fastapi | Async REST API framework with automatic OpenAPI docs |
| **uvicorn** | >=0.29.0 | BSD-3-Clause | https://github.com/encode/uvicorn | Production-grade ASGI server |
| **pydantic** | >=2.6.0 | MIT | https://github.com/pydantic/pydantic | Type validation and schema serialization |
| **pydantic-settings** | >=2.2.0 | MIT | https://github.com/pydantic/pydantic-settings | Environment and config management |
| **python-multipart** | >=0.0.9 | Apache-2.0 | https://github.com/Kludex/python-multipart | Multipart form file upload parsing for FastAPI |
| **pypdfium2** | >=4.30.0 | Apache-2.0 / BSD-3-Clause | https://github.com/pypdfium2-team/pypdfium2 | PDF page rendering to images; non-copyleft alternative to PyMuPDF |
| **pdfplumber** | >=0.11.0 | MIT | https://github.com/jsvine/pdfplumber | PDF text and table extraction without AGPL |
| **rapidocr-onnxruntime** | >=1.3.0 | Apache-2.0 | https://github.com/RapidAI/RapidOCR | Self-contained CPU OCR engine with bounding boxes |
| **onnxruntime** | >=1.17.0 | MIT | https://github.com/microsoft/onnxruntime | Fast ONNX inference backend for RapidOCR on CPU |
| **pillow** | >=10.2.0 | HPND (MIT-equivalent) | https://github.com/python-pillow/Pillow | Image loading, resizing, security decompression checks |
| **opencv-python-headless** | >=4.9.0 | Apache-2.0 | https://github.com/opencv/opencv-python | Image preprocessing, deskewing, blur detection |
| **rapidfuzz** | >=3.6.0 | MIT | https://github.com/rapidfuzz/RapidFuzz | Fast fuzzy string matching for token grounding |
| **reportlab** | >=4.1.0 | BSD-3-Clause | https://github.com/Distrotech/reportlab | Programmatic generation of PDF audit reports & synthetic documents |
| **faker** | >=24.0.0 | MIT | https://github.com/joke2k/faker | Generation of synthetic financial and personal names |
| **numpy** | >=1.26.0 | BSD-3-Clause | https://github.com/numpy/numpy | Array math and matrix transformations |
| **scipy** | >=1.12.0 | BSD-3-Clause | https://github.com/scipy/scipy | Bootstrap confidence interval calculation |
| **matplotlib** | >=3.8.0 | Matplotlib (PSF compatible) | https://github.com/matplotlib/matplotlib | Generation of research benchmark plots |
| **pytest** | >=8.0.0 | MIT | https://github.com/pytest-dev/pytest | Unit and integration testing framework |
| **pytest-cov** | >=4.1.0 | MIT | https://github.com/pytest-dev/pytest-cov | Code coverage tracking and reporting |
| **httpx** | >=0.27.0 | BSD-3-Clause | https://github.com/encode/httpx | Async HTTP client for integration testing |
| **psutil** | >=5.9.0 | BSD-3-Clause | https://github.com/giampaolo/psutil | Hardware resource profiling (RAM, CPU) |

---

## Frontend Libraries (UI)

| Name | Specified Version | License | Source Repository | Purpose / Reason Chosen |
|---|---|---|---|---|
| **React** | ^18.3.1 | MIT | https://github.com/facebook/react | Reactive user interface |
| **React DOM** | ^18.3.1 | MIT | https://github.com/facebook/react | DOM rendering |
| **Vite** | ^5.2.0 | MIT | https://github.com/vitejs/vite | Fast frontend bundler and development server |
| **TypeScript** | ^5.4.0 | Apache-2.0 | https://github.com/microsoft/TypeScript | Static type safety |
| **Tailwind CSS** | ^3.4.0 | MIT | https://github.com/tailwindlabs/tailwindcss | Utility-first CSS styling system |
| **Lucide React** | ^0.363.0 | ISC | https://github.com/lucide-icons/lucide | Modern accessible UI icon set |
| **clsx / tailwind-merge**| ^2.0.0 | MIT | https://github.com/lukeed/clsx | Conditional class merging |

---

## Vision-Language Model (Optional / Colab)

| Name | Source | License | Purpose |
|---|---|---|---|
| **Qwen2-VL-2B-Instruct** | Qwen / Alibaba Cloud | Apache-2.0 | Lightweight vision-language model used for optional GPU fine-tuning experiments in Colab |
