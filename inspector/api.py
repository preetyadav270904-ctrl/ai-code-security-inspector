from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from inspector import config
from inspector.models import ScanReport, CodePayload
from inspector.core import scan_source

app = FastAPI(
    title="Security Inspector API",
    version="1.0.0",
    docs_url="/docs",
)

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "index.html"


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    """Serves the single-page developer dashboard."""
    if not TEMPLATE_PATH.is_file():
        raise HTTPException(status_code=500, detail="Dashboard template missing.")
    return HTMLResponse(content=TEMPLATE_PATH.read_text(encoding="utf-8"))


@app.get("/health")
def health():
    return {"status": "up", "model": config.MODEL_NAME}


@app.post("/scan", response_model=ScanReport)
def scan_snippet(payload: CodePayload):
    try:
        return scan_source(payload.source, file_name=payload.file_name)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.post("/scan/file", response_model=ScanReport)
async def scan_file_upload(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Only UTF-8 text files supported.")

    try:
        return scan_source(decoded, file_name=file.filename or "upload.py")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))