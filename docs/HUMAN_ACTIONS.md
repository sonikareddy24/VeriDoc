# Action Needed From User Log

This document records all tasks that require manual user intervention (e.g. system binary installs, GPU execution in Google Colab, external approvals).

---

## Active Action Items

### ACTION-001: (Optional) Run VLM LoRA Fine-Tuning on Free Google Colab GPU

**Description**:
To explore Vision-Language Model (VLM) fine-tuning on a free GPU and evaluate Qwen2-VL-2B-Instruct against the deterministic OCR baseline, execute the provided notebook on Google Colab.

**Exact Steps**:
1. Open Google Colab (https://colab.research.google.com).
2. Click **File** -> **Upload notebook**, and upload `colab/finetune_vlm_lora.ipynb` from this repo.
3. In Colab, click **Runtime** -> **Change runtime type**, select **T4 GPU** (100% free), and click **Save**.
4. Run all cells in the notebook. The script will load Qwen2-VL-2B-Instruct in 4-bit with PEFT LoRA, train on seen-layout documents, and generate prediction files.
5. Download the output directory `predictions/` from Colab into your local workspace at `data/predictions/`.
6. To notify the assistant, simply reply in chat: "I have downloaded VLM predictions to data/predictions/".

**Expected Result**:
`data/predictions/*.json` prediction files present in repo, allowing the evaluation benchmark to evaluate B2/B3 VLM pipelines locally.

**Fallback**:
If you choose not to run Colab, the entire project, evaluation benchmark, and web application remain 100% operational using the default B1 CPU OCR engine (`ocr_rules`).
