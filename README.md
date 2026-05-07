# CSC 483 – Building Part of Watson

This project implements a simplified Watson-style Jeopardy question-answering system using Python and the Whoosh IR library.

The system indexes approximately **280,000 Wikipedia pages** and attempts to answer Jeopardy clues by retrieving the most relevant Wikipedia page title.

---

# Setup

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Add Required Data Files

Place the Jeopardy questions file at:

```text
data/questions.txt
```

Place the extracted Wikipedia files inside:

```text
data/wiki/
```

---

# Build the Index

Run the index builder before evaluating the system.

```bash
python build_index.py
```

---

# Evaluate the System

Run the evaluation script after the index has been built.

```bash
python evaluate.py
```

---

# Output Files

Evaluation results are saved in:

```text
results/predictions.csv
results/metrics.txt
```
