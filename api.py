from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from projects.clump_stylizer.curly_pipeline import generate_strands
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI()

# Garante que a pasta 'output' exista
os.makedirs("output", exist_ok=True)

# Expõe a pasta como arquivos estáticos na rota /output
app.mount("/output", StaticFiles(directory="output"), name="output")

# Permitir chamadas do frontend local (ex: localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique o domínio correto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dados esperados no corpo da requisição
class HairParams(BaseModel):
    guidePath: str
    scalpPath: str
    groupingCSV: str
    outputPath: str = "output/strands.obj"

# Rota principal para gerar os fios
@app.post("/generate")
async def generate_hair(params: HairParams):
    strands = generate_strands(
        guide_path=params.guidePath,
        scalp_path=params.scalpPath,
        grouping_csv=params.groupingCSV,
        output_path=params.outputPath
    )
    return {"strands": strands}
