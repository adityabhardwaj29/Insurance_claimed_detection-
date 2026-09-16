from fastapi import FastAPI
app=FastAPI(title="Graph Enhanced Insurance Claim Detection API")

@app.get("/health")
def health():
    return {"status":"ok"}
