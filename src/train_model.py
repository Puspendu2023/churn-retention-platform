"""Model training: compares candidate classifiers with stratified CV on the TRAINING set only,
then fits the chosen model and serialises it to models/churn_model.pkl."""
import json
import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from src.data_prep import (ROOT, load_raw, clean, get_split, build_preprocessor, RANDOM_STATE)

MODEL_PATH = ROOT / "models" / "churn_model.pkl"
CV_PATH = ROOT / "models" / "cv_results.json"

CANDIDATES = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
    "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=10,
                                            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=150, max_depth=2, learning_rate=0.05,
                                                    random_state=RANDOM_STATE),
}
CHOSEN = "Logistic Regression"


def make_pipeline(name):
    return Pipeline([("prep", build_preprocessor()), ("clf", CANDIDATES[name])])


def main():
    df = clean(load_raw())
    X_train, X_test, y_train, y_test = get_split(df)
    print(f"Train {len(X_train)} rows, test {len(X_test)} rows, train churn rate {y_train.mean():.3f}, test {y_test.mean():.3f}")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    results = {}
    for name in CANDIDATES:
        s = cross_validate(make_pipeline(name), X_train, y_train, cv=cv,
                           scoring=["roc_auc", "recall", "precision", "f1", "accuracy"])
        results[name] = {k.replace("test_", ""): float(np.mean(v)) for k, v in s.items() if k.startswith("test_")}
        print(name, {k: round(v, 3) for k, v in results[name].items()})
    CV_PATH.write_text(json.dumps(results, indent=2))
    model = make_pipeline(CHOSEN).fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved {CHOSEN} to {MODEL_PATH}")


if __name__ == "__main__":
    main()
