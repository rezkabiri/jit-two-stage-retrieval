# app/main.py
import os
import sys
import uvicorn
from google.adk import App

print("🚀 Starting container boot sequence...")

try:
    # Use absolute imports to ensure package consistency
    from app.agent import root_agent
    print("✅ Root agent imported successfully.")

    # Create the ADK App
    print("⏳ Initializing ADK App...")
    app = App(root_agent=root_agent, name="app")
    print("✅ ADK App initialized.")

except Exception as e:
    print(f"❌ FATAL ERROR during startup: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    # Cloud Run provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    print(f"📡 Server starting to listen on port {port}...")
    # Run the server directly
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
