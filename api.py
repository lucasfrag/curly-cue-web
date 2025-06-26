from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta a pasta 'output' como estática (para acessar strands.obj/mtl)
output_dir = os.path.join(os.path.dirname(__file__), "output")
app.mount("/output", StaticFiles(directory=output_dir), name="output")

# Monta a pasta 'data' como estática (para acessar scalpPath direto via URL)
data_dir = os.path.join(os.path.dirname(__file__), "data")
app.mount("/data", StaticFiles(directory=data_dir), name="data")


# Modelo para requisição
class HairRequest(BaseModel):
    guidePath: str
    scalpPath: str
    groupingCSV: str
    outputPath: str
    curliness: float
    length: float
    density: float
    color: str


@app.post("/generate")
async def generate_hair(req: HairRequest):
    cmd = [
        "python", "wispify.py",
        req.guidePath,
        req.scalpPath,
        req.groupingCSV,
        req.outputPath,
        "--curliness", str(req.curliness),
        "--length", str(req.length),
        "--density", str(req.density),
        "--color", req.color
    ]
    try:
        subprocess.run(cmd, check=True)
        return {"message": "Geração concluída com sucesso."}
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}
