from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # <-- Yeh line add karein
from pydantic import BaseModel
import subprocess
import os
import uuid

app = FastAPI(title="MP4 to M3U8 Converter API")

# CORS Configuration: Sabhi origins ko allow karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production me aap ise specific domain par restrict kar sakte hain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=OUTPUT_DIR), name="media")

class ConvertRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"message": "MP4 to M3U8 Converter API is running!"}

@app.post("/convert")
async def convert_to_hls(request_data: ConvertRequest, request: Request):
    try:
        unique_folder = f"hls_{uuid.uuid4().hex[:10]}"
        folder_path = os.path.join(OUTPUT_DIR, unique_folder)
        os.makedirs(folder_path, exist_ok=True)
        
        output_file = os.path.join(folder_path, "master.m3u8")
        
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
        
        base_url = str(request.base_url).rstrip('/')
        m3u8_absolute_url = f"{base_url}/media/{unique_folder}/master.m3u8"
        
        return {
            "status": "success",
            "message": "Conversion successful",
            "m3u8_url": m3u8_absolute_url
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
