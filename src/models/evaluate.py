from sklearn.metrics import classification_report, roc_auc_score
def evaluate(model, X, y):
    pred=model.predict(X)
    result={"classification_report": classification_report(y,pred,output_dict=True)}
    if hasattr(model,"predict_proba"):
        result["roc_auc"]=roc_auc_score(y,model.predict_proba(X)[:,1])
    return result
