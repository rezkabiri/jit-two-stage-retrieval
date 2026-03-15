# app/main.py
import os
from fastapi import FastAPI

print("🚀 BARE BONES STARTUP")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable provided by Cloud Run
    port = int(os.environ.get("PORT", 8080))
    print(f"📡 Listening on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
