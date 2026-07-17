# Purpose:
# This is the main FastAPI entrypoint for the backend application.
# It is the file that starts the API server and becomes the first place
# where routes, middleware, health checks, and app-level configuration connect together.


from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.protected import router as protected_router


app = FastAPI(title="ClinicSense AI")

app.include_router(auth_router)
app.include_router(protected_router)


@app.get("/")
def health():
    return {"status": "ok", "message": "ClinicSense backend running"}