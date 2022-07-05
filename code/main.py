from cgitb import html
from ctypes.wintypes import HMETAFILE
from enum import EnumMeta
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=18081, reload=True)