#from cgitb import html
#from ctypes.wintypes import HMETAFILE
#from enum import EnumMeta
from pathlib import Path
import uvicorn

if __name__ == "__main__":
    cwd = Path(__file__).parent.resolve()
    uvicorn.run("api:app", host="0.0.0.0", port=18081, reload=True, log_config=f"{cwd}/log.ini")    
    #uvicorn.run("api:app", host="0.0.0.0", port=18081, reload=True)
    