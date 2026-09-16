# Graph Enhanced — Insurance Claim Detection

This is a complete academic/demo project architecture for graph-enhanced insurance claim anomaly/fraud detection.

## Pipeline
Raw data -> cleaning -> feature engineering -> duplicate detection + ML + anomaly detection -> graph construction/features -> risk score -> investigation cases -> API/dashboard.

## Dataset
The included dataset is **synthetic demo data** created for development/testing. It is not real insurance data.

## Run
1. Create a virtual environment.
2. Install requirements.
3. Start API: `uvicorn api.main:app --reload`
4. Start dashboard: `streamlit run dashboard/app.py`

## Important
The `fraud_label` field is synthetic ground truth for demonstration and model-development testing; it must not be represented as real-world fraud evidence.
