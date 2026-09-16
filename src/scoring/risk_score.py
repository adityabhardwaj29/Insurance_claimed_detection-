def calculate_risk_score(ml_probability, anomaly_score, duplicate_score, graph_risk):
    values=[ml_probability, anomaly_score, duplicate_score, graph_risk]
    return round(sum(values)/len(values),4)
