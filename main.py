from fastapi import FastAPI, UploadFile, Form
import os

from parse_dxf import extract_entities
from generate_ifc import create_basic_ifc

app = FastAPI()

@app.post("/convert")
async def convert(
    file: UploadFile,
    units: str = Form(...),
    wall_height: float = Form(...),
    layers: str = Form(...)
):
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Si es DWG, aquí iría la conversión. Por ahora asumimos DXF.
    if not file_path.endswith(".dxf"):
        return {"error": "Solo se aceptan archivos .dxf por ahora."}

    # Leer geometría
    geometry = extract_entities(file_path, layers.split(","))

    # Crear IFC (aún sin geometría real)
    ifc_path = create_basic_ifc()

    return {
        "entities": geometry[:5],  # Devuelve las primeras 5 entidades como muestra
        "ifc_generated": True,
        "download_url": f"/outputs/{os.path.basename(ifc_path)}"
    }
