from pathlib import Path
import uvicorn

if __name__ == "__main__":
   cwd = Path(__file__).parent.resolve()
   uvicorn.run("api_webhooks:app_wh", host="0.0.0.0", port=18082, reload=True, log_config=f"{cwd}/logwh.ini")