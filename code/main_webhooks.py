import uvicorn

if __name__ == "__main__":
   uvicorn.run("api_webhooks:app_wh", host="0.0.0.0", port=18082, reload=True)