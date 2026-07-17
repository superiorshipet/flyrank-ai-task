from fastapi import FastAPI

app = FastAPI(
    title="Task API",
    description="Simple CRUD API for managing tasks",
    version="1.0"
)


@app.get("/", summary="API Information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Health Check")
def health():
    return {
        "status": "ok"
    }