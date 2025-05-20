from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from notifier import notify
import subprocess, os, json
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse

app.mount("/", StaticFiles(directory="static", html=True), name="static")

API_TOKEN = "secret123"  # change or load from ENV

app = FastAPI(title="Passive Recon API")

class ReconRequest(BaseModel):
    domain: str
    webhook_url: str = None
    slack_webhook: str = None
    email: str = None
    push_key: str = None
    push_token: str = None


@app.post("/recon")
def run_recon(req: ReconRequest, authorization: str = Header(...)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    domain_dir = f"/data/history/{req.domain}"
    os.makedirs(domain_dir, exist_ok=True)
    output_file = f"{domain_dir}/{timestamp}.txt"

    # Run passive recon
    subprocess.run(["amass", "enum", "-passive", "-d", req.domain, "-o", output_file])

    with open(output_file) as f:
        results = f.read()

    # Optional index logging
    index_path = f"{domain_dir}/index.json"
    index = []
    if os.path.exists(index_path):
        with open(index_path) as idx:
            index = json.load(idx)

    entry = {
        "timestamp": timestamp,
        "output_file": output_file,
        "line_count": results.count('\n'),
        "domain": req.domain
    }

    index.append(entry)
    with open(index_path, "w") as idx:
        json.dump(index, idx, indent=2)

    notify(results, req)

    return {
        "status": "completed",
        "domain": req.domain,
        "lines_found": entry["line_count"],
        "file": output_file,
        "timestamp": timestamp
    }

@app.get("/history/{domain}")
def get_history(domain: str, authorization: str = Header(...)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    index_path = f"/data/history/{domain}/index.json"
    if not os.path.exists(index_path):
        return JSONResponse(status_code=404, content={"detail": "No history found for this domain"})

    with open(index_path) as idx:
        index = json.load(idx)

    return {"domain": domain, "history": index}

@app.get("/history/{domain}/{timestamp}", response_class=PlainTextResponse)
def get_scan_result(domain: str, timestamp: str, authorization: str = Header(...)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    file_path = f"/data/history/{domain}/{timestamp}.txt"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Scan not found")

    with open(file_path, "r") as f:
        content = f.read()

    return content
