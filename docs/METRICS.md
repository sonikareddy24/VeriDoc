# VeriDocs AI — Metric Definitions & Research Evaluation Formulation

This document defines the mathematical formulation of all evaluation metrics utilized in VeriDocs AI benchmarks.

---

## 1. Field Extraction Metrics

Let $\mathcal{D} = \{ (x_i, y_i) \}_{i=1}^N$ be the evaluation dataset of documents, where each document contains a set of ground-truth fields $y_i = \{ (f, v_f^*) \}_{f \in \mathcal{F}}$ and corresponding extracted predictions $\hat{y}_i = \{ (f, \hat{v}_f) \}_{f \in \mathcal{F}}$.

### 1.1 Field Exact-Match Accuracy
A field $f$ is considered an exact match if its normalized value matches ground truth within a numeric float tolerance $\epsilon = 0.05$ (for currency) or exact string equality:
$$\text{Correct}(f) = \begin{cases} 
1 & \text{if } |\hat{v}_f - v_f^*| \le 0.05 \quad (\text{numeric}) \\
1 & \text{if } \text{norm}(\hat{v}_f) = \text{norm}(v_f^*) \quad (\text{string}) \\
0 & \text{otherwise}
\end{cases}$$

$$\text{Field Accuracy} = \frac{\sum_{i=1}^N \sum_{f \in y_i} \text{Correct}(f)}{\sum_{i=1}^N |y_i|}$$

### 1.2 Normalized Levenshtein Edit Distance (Text Fields)
$$\text{NLED}(s_1, s_2) = \frac{\text{Levenshtein}(s_1, s_2)}{\max(|s_1|, |s_2|)}$$

---

## 2. Verification & Safety Metrics (Headline)

Let $\mathcal{S}(\hat{v}_f) \in \{ \text{Supported}, \text{Inconsistent}, \text{Uncertain}, \text{Unreadable} \}$ denote the status assigned to an extracted field by the verification engine.

### 2.1 Undetected Error Rate (Headline Metric)
The primary risk in document intelligence is an extraction error that goes undetected and is falsely presented as verified ("Supported") to downstream systems:
$$\text{Undetected Error Rate} = \frac{\sum_{i=1}^N \sum_{f \in y_i} \mathbb{I}(\text{Correct}(f) = 0 \land \mathcal{S}(\hat{v}_f) = \text{Supported})}{\sum_{i=1}^N \sum_{f \in y_i} \mathbb{I}(\text{Correct}(f) = 0)}$$

*Interpretation*: What fraction of incorrect fields does the pipeline fail to catch? A lower rate indicates superior safety.

### 2.2 Coverage Cost
To prevent gaming the headline metric by simply marking every field as "Uncertain" or "Inconsistent", coverage cost tracks the proportion of genuinely correct fields that are successfully retained as "Supported":
$$\text{Coverage Rate} = \frac{\sum_{i=1}^N \sum_{f \in y_i} \mathbb{I}(\text{Correct}(f) = 1 \land \mathcal{S}(\hat{v}_f) = \text{Supported})}{\sum_{i=1}^N \sum_{f \in y_i} \mathbb{I}(\text{Correct}(f) = 1)}$$

### 2.3 False-Alarm Rate
The fraction of correct fields that are erroneously marked "Inconsistent":
$$\text{False-Alarm Rate} = \frac{\sum_{i=1}^N \sum_{f \in y_i} \mathbb{I}(\text{Correct}(f) = 1 \land \mathcal{S}(\hat{v}_f) = \text{Inconsistent})}{\sum_{i=1}^N \sum_{f \in y_i} \mathbb{I}(\text{Correct}(f) = 1)}$$

---

## 3. Seeded Inconsistency Detection (Document Level)

Seeded inconsistencies simulate arithmetic manipulation, date inversions, and bank running balance breaks.

$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
$$\text{FPR} = \frac{FP}{FP + TN}, \quad \text{FNR} = \frac{FN}{FN + TP}$$

*Benign Variations*: Realistic variations (wire fees, partial disbursements, clearing delays) are included as negative cases ($y = 0$). Flagging them as "Inconsistent" counts as a false positive ($FP$); classifying them as "Uncertain" preserves $TN$.

---

## 4. Bootstrap Confidence Intervals

To account for document-level correlation and sample variance, 95% confidence intervals are computed using non-parametric percentile bootstrapping:
1. Resample $N$ documents with replacement $B = 1,000$ times.
2. Recompute metric $\hat{\theta}^{(b)}$ for each bootstrap sample $b \in \{1, \dots, B\}$.
3. Compute the 2.5th and 97.5th percentiles:
   $$\text{CI}_{95} = \left[ Q(0.025), Q(0.975) \right]$$

---

## 5. Tuning Discipline Statement
All heuristic layout parsing rules (label proximity regexes, table column coordinates, line grouping thresholds) were tuned strictly on the **Seen Layouts** development split (Layouts 1 and 2). At no point during rule development were Unseen Layouts (Layouts 3 and 4) inspected or used for threshold tuning.
