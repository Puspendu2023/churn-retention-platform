"""Evaluate the saved model on the held-out test set; write metrics + figures."""
import json
import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, roc_auc_score, roc_curve)
from src.data_prep import ROOT, load_raw, clean, get_split
from src.train_model import MODEL_PATH

DOCS = ROOT / "docs"
FIG = DOCS / "figures"


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    df = clean(load_raw())
    X_train, X_test, y_train, y_test = get_split(df)
    model = joblib.load(MODEL_PATH)
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    m = {
        "n_test": int(len(y_test)), "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred), "recall": recall_score(y_test, pred),
        "f1": f1_score(y_test, pred), "roc_auc": roc_auc_score(y_test, proba),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "majority_baseline_accuracy": float(1 - y_test.mean()),
    }
    # Risk-band distribution on test set (Low <0.35, Medium 0.35-0.55, High >=0.55)
    bands = np.where(proba >= 0.55, "High", np.where(proba >= 0.35, "Medium", "Low"))
    m["bands"] = {b: {"n": int((bands == b).sum()), "actual_churn_rate": float(y_test[bands == b].mean())}
                  for b in ["Low", "Medium", "High"] if (bands == b).any()}
    # Coefficients
    prep, clf = model.named_steps["prep"], model.named_steps["clf"]
    names = [n.split("__")[1] for n in prep.get_feature_names_out()]
    coefs = sorted(zip(names, clf.coef_[0]), key=lambda t: t[1])
    m["coefficients"] = {n: float(c) for n, c in coefs}
    (ROOT / "models" / "metrics.json").write_text(json.dumps(m, indent=2))
    print(json.dumps({k: v for k, v in m.items() if k != "coefficients"}, indent=2))

    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    cm = np.array([[tn, fp], [fn, tp]])
    ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=16,
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Pred: Stay", "Pred: Churn"]); ax.set_yticklabels(["Actual: Stay", "Actual: Churn"])
    ax.set_title("Confusion matrix (test set, n=%d)" % len(y_test), fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "confusion_matrix.png", dpi=180); plt.close(fig)

    fpr, tpr, _ = roc_curve(y_test, proba)
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    ax.plot(fpr, tpr, color="#1f4e79", label=f"AUC = {m['roc_auc']:.3f}")
    ax.plot([0, 1], [0, 1], "--", color="grey", label="Random guess")
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_title("ROC curve (test set)", fontsize=10); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / "roc_curve.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.4))
    ns, cs = zip(*coefs)
    ax.barh(ns, cs, color=["#c0392b" if c > 0 else "#2e86c1" for c in cs])
    ax.axvline(0, color="black", lw=0.8)
    ax.set_title("Logistic Regression coefficients (standardised features)", fontsize=10)
    ax.set_xlabel("Coefficient (red = raises churn risk)")
    fig.tight_layout(); fig.savefig(FIG / "coefficients.png", dpi=180); plt.close(fig)


if __name__ == "__main__":
    main()
