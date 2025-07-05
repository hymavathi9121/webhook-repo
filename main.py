from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()
webhook_data = []

@app.post("/webhook")
async def webhook_listener(request: Request):
    data = await request.json()
    data["received_at"] = datetime.utcnow().isoformat()

    # Avoid duplicates
    if data not in webhook_data:
        webhook_data.append(data)
    
    return {"message": "Received"}

@app.get("/", response_class=HTMLResponse)
def show_data():
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    filtered = [
        item for item in webhook_data 
        if datetime.fromisoformat(item["received_at"]) > cutoff
    ]

    html = "<h2>Webhook Data (last 5 mins)</h2><ul>"
    for item in filtered:
        html += f"<li>{item}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
