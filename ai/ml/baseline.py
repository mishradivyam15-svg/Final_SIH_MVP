"""
TF-IDF + Logistic Regression baseline for safety-signal classification.

Experiment BL: classical NLP baseline using only scikit-learn.
"""

import os
import sys
import time

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ai.ml.dataset import (
    load_all_rows, split_rows, SafetyDataset,
    HAZARD_LABELS, EXPOSURE_LABELS, HAZARD_TO_IDX, EXPOSURE_TO_IDX,
)
from ai.ml.evaluate import evaluate_and_save


DATA_PATH = os.path.join(REPO_ROOT, "data", "labeled", "training_labels.csv")
RESULTS_DIR = os.path.join(REPO_ROOT, "models", "safety_classifier", "results",
                           "BL_tfidf_lr")


def run_baseline():
    """Run TF-IDF + Logistic Regression baseline."""
    print("=" * 60)
    print("  Experiment BL: TF-IDF + Logistic Regression")
    print("=" * 60)
    print()

    # Load data with high + medium confidence for train
    all_rows = load_all_rows(DATA_PATH)
    train_rows, val_rows, test_rows = split_rows(
        all_rows, confidence_filter={"high", "medium"}
    )

    print(f"Train rows: {len(train_rows):,}")
    print(f"Val rows:   {len(val_rows):,}")
    print(f"Test rows:  {len(test_rows):,}")
    print()

    # Extract texts and labels
    def extract(rows):
        texts, haz, exp = [], [], []
        for r in rows:
            t = r.get("Final Narrative", "").strip()
            if not t:
                continue
            texts.append(t)
            h = r.get("hazard_label", "").strip() or "null"
            e = r.get("exposure_label", "").strip() or "null"
            haz.append(HAZARD_TO_IDX.get(h, 0))
            exp.append(EXPOSURE_TO_IDX.get(e, 0))
        return texts, np.array(haz), np.array(exp)

    train_texts, train_haz, train_exp = extract(train_rows)
    test_texts, test_haz, test_exp = extract(test_rows)

    print(f"Train texts: {len(train_texts):,}")
    print(f"Test texts:  {len(test_texts):,}")
    print()

    start = time.time()

    # TF-IDF
    print("Fitting TF-IDF vectorizer...")
    tfidf = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        strip_accents="unicode",
        min_df=2,
    )
    X_train = tfidf.fit_transform(train_texts)
    X_test = tfidf.transform(test_texts)

    # Hazard classifier
    print("Training hazard classifier...")
    haz_clf = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        multi_class="multinomial",
        n_jobs=-1,
    )
    haz_clf.fit(X_train, train_haz)
    haz_preds = haz_clf.predict(X_test)

    # Exposure classifier
    print("Training exposure classifier...")
    exp_clf = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        multi_class="multinomial",
        n_jobs=-1,
    )
    exp_clf.fit(X_train, train_exp)
    exp_preds = exp_clf.predict(X_test)

    train_time = time.time() - start
    print(f"\nTraining time: {train_time:.1f}s")

    # Evaluate
    summary = evaluate_and_save(
        "BL: TF-IDF + Logistic Regression",
        test_haz.tolist(), haz_preds.tolist(),
        test_exp.tolist(), exp_preds.tolist(),
        RESULTS_DIR,
        training_time=train_time,
    )

    return summary


if __name__ == "__main__":
    run_baseline()
