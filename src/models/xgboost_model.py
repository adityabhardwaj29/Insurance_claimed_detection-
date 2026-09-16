from xgboost import XGBClassifier
def build_model():
    return XGBClassifier(
        n_estimators=250, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, eval_metric="logloss"
    )
