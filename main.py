from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os
import uuid

app = FastAPI()

class ConvertRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"message": "MP4 to M3U8 Converter API Running!"}

@app.post("/convert")
def convert(request: ConvertRequest):
    try:
        folder = f"hls_{uuid.uuid4().hex[:8]}"
        os.makedirs(folder, exist_ok=True)
        output = os.path.join(folder, "master.m3u8")

        cmd = [
            "ffmpeg", "-i", request.url,
            "-c", "copy",
            "-hls_time", "6",
            "-hls_list_size", "0",
            "-f", "hls",
            output
        ]
        subprocess.run(cmd, check=True)

        return {
            "status": "success",
            "m3u8_url": f"/{folder}/master.m3u8"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
