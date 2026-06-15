from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os
import uuid

app = FastAPI(title="MP4 to M3U8 Converter API")

# Ek standard directory banayein jahan saare HLS folders save honge
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Is directory ko static files ki tarah mount karein taaki media URLs access ho sakein
app.mount("/media", StaticFiles(directory=OUTPUT_DIR), name="media")

class ConvertRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"message": "MP4 to M3U8 Converter API is running!"}

@app.post("/convert")
async def convert_to_hls(request_data: ConvertRequest, request: Request):
    try:
        # Har request ke liye unique sub-folder banayein 'outputs' ke andar
        unique_folder = f"hls_{uuid.uuid4().hex[:10]}"
        folder_path = os.path.join(OUTPUT_DIR, unique_folder)
        os.makedirs(folder_path, exist_ok=True)
        
        output_file = os.path.join(folder_path, "master.m3u8")
        
        # FFmpeg command
        command = [
            "ffmpeg",
            "-i", request_data.url,
            "-c", "copy",
            "-hls_time", "6",
            "-hls_list_size", "0",
            "-f", "hls",
            output_file
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        
        # Base URL nikalein (e.g., https://api-production-...railway.app)
        base_url = str(request.base_url).rstrip('/')
        m3u8_absolute_url = f"{base_url}/media/{unique_folder}/master.m3u8"
        
        return {
            "status": "success",
            "message": "Conversion successful",
            "m3u8_url": m3u8_absolute_url
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
