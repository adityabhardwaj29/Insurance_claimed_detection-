from fastapi import FastAPI
from api.routes.cases import router as cases_router

app = FastAPI(title="Graph Enhanced Insurance Claim Detection API")
app.include_router(cases_router)


@app.get("/health")
def health():
    return {"status": "ok"}
